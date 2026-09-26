"""
Per-host circuit breaker, opened when a data source refuses access.

After one request is blocked, later requests to the same host stop where they
are, without opening a connection, until the cooldown expires. The point is to
keep a loop over a symbol list from firing dozens more requests at a server that
just said, in as many words, to stop.

Two design choices worth keeping:

1. **The key covers the egress, not just the hostname.** Being blocked is tied to
   the IP address in use. Keying on hostname alone would mean one block on a
   direct call also shuts down the route through a proxy - closing off the exact
   escape hatch the user needs. The reverse holds too: a dirty proxy must not
   cost the user their direct access.

2. **Sharing state across threads is deliberate.** Sessions are kept per-thread
   because requests.Session is not thread-safe, but the breaker earns its keep
   precisely by letting a third thread learn from what the first one just hit.
   Do not "fix" this asymmetry.
"""

import os
import threading
import time
from urllib.parse import urlsplit

from vnstock.config import Config

__all__ = [
    "circuit_check",
    "circuit_key",
    "circuit_status",
    "circuit_trip",
    "reset_circuit",
]

# Key -> expiry instant on time.monotonic().
# A monotonic clock, not time.time(): neither an NTP resync nor a user changing
# the system clock can leave the breaker stuck open for hours.
_deadlines: dict[str, float] = {}
_lock = threading.Lock()

_COOLDOWN_BY_KIND = {
    "rate_limit": "BLOCK_COOLDOWN_RATE_LIMIT",
    "challenge": "BLOCK_COOLDOWN_CHALLENGE",
    "denied": "BLOCK_COOLDOWN_DENIED",
}

_FALSY = {"0", "off", "false", "no"}

# The breaker started life in vnstock_data. Keep reading the old variable name so
# that anyone switching it off through VNSTOCK_DATA_CIRCUIT_BREAKER does not find
# it silently switched back on once the shared code moved down into vnstock.
_ENV_SWITCHES = ("VNSTOCK_CIRCUIT_BREAKER", "VNSTOCK_DATA_CIRCUIT_BREAKER")


def circuit_enabled() -> bool:
    """Report whether the breaker is currently active.

    Reads the environment variable at call time rather than remembering it from
    import, so a Jupyter user can switch it off mid-session without restarting
    the kernel.
    """
    for name in _ENV_SWITCHES:
        raw = os.environ.get(name)
        if raw is not None and raw.strip().lower() in _FALSY:
            return False
    return bool(Config.CIRCUIT_BREAKER_ENABLED)


def circuit_key(url: str, proxies: dict[str, str] | None = None) -> str:
    """Build a breaker key shaped "host|egress".

    Reads .hostname rather than .netloc for the proxy, so proxy credentials never
    reach the key, the logs, or an error message.
    """
    host = (urlsplit(url).netloc or "").lower()
    egress = "direct"
    if proxies:
        proxy_url = proxies.get("https") or proxies.get("http") or ""
        if proxy_url:
            egress = (urlsplit(proxy_url).hostname or "proxy").lower()
    return f"{host}|{egress}"


def cooldown_for(signal) -> float:
    """Work out the cooldown for one block signal, clamped at both ends."""
    seconds = None
    retry_after = getattr(signal, "retry_after", None)
    if retry_after and retry_after > 0:
        seconds = float(retry_after)
    if seconds is None:
        attr = _COOLDOWN_BY_KIND.get(
            getattr(signal, "kind", ""), "BLOCK_COOLDOWN_DENIED"
        )
        seconds = float(getattr(Config, attr))
    # Clamping is also what keeps an unreasonably long Retry-After in check.
    return max(Config.BLOCK_COOLDOWN_MIN, min(seconds, Config.BLOCK_COOLDOWN_MAX))


def circuit_check(key: str) -> float | None:
    """Return the seconds left if the breaker is open, None if calls may proceed."""
    if not circuit_enabled():
        return None
    now = time.monotonic()
    with _lock:
        deadline = _deadlines.get(key)
        if deadline is None:
            return None
        if deadline <= now:
            _deadlines.pop(key, None)
            return None
        return deadline - now


def circuit_trip(key: str, signal) -> float:
    """Open the breaker for one key. Returns the cooldown applied."""
    cooldown = cooldown_for(signal)
    if not circuit_enabled():
        return cooldown
    now = time.monotonic()
    with _lock:
        _prune_locked(now)
        # Keep the later deadline: a heavy signal must not be overwritten by a
        # lighter one.
        current = _deadlines.get(key, 0.0)
        _deadlines[key] = max(current, now + cooldown)
    return cooldown


def _prune_locked(now: float) -> None:
    """Reclaim breaker memory. Only call while holding the lock."""
    if len(_deadlines) < Config.CIRCUIT_MAX_ENTRIES:
        return
    for key in [k for k, deadline in _deadlines.items() if deadline <= now]:
        _deadlines.pop(key, None)
    # Still full: drop the entries closest to expiring first.
    overflow = len(_deadlines) - Config.CIRCUIT_MAX_ENTRIES + 1
    if overflow > 0:
        for key, _ in sorted(_deadlines.items(), key=lambda item: item[1])[:overflow]:
            _deadlines.pop(key, None)


def circuit_status() -> dict[str, float]:
    """List the hosts currently on cooldown, with the seconds left on each."""
    now = time.monotonic()
    with _lock:
        return {
            key: deadline - now
            for key, deadline in _deadlines.items()
            if deadline > now
        }


def reset_circuit(host: str | None = None) -> int:
    """Clear cooldown state so calls may resume immediately.

    Use this once you have switched network or proxy and want to try again
    without waiting the cooldown out.

    Args:
        host: Hostname to clear. Leave empty to clear everything.

    Returns:
        Number of entries cleared.
    """
    with _lock:
        if host is None:
            count = len(_deadlines)
            _deadlines.clear()
            return count
        needle = host.lower()
        matched = [key for key in _deadlines if key.split("|", 1)[0] == needle]
        for key in matched:
            _deadlines.pop(key, None)
        return len(matched)
