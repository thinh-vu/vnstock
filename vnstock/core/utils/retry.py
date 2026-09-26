"""
Shared retry policy for the API adapter layer.

Only transient failures deserve a retry. Permanent ones - a source that does not
implement a method, an invalid argument, an empty result - must surface straight
away carrying their own message. Retrying them wastes the user's time and their
rate-limit quota, and the tenacity ``RetryError`` wrapper hides the explanation
the library took care to write (e.g. "KBS không cung cấp ICB classification.
Sử dụng symbols_by_industries()").

``reraise=True`` keeps that guarantee for retryable errors too: once the attempts
run out the original exception propagates instead of a ``RetryError``.

The decision is a predicate rather than ``retry_if_exception_type`` because the
two categories overlap by inheritance. ``DataSourceBlockedError`` derives from
``ConnectionError`` on purpose, so that pre-existing ``except ConnectionError``
code keeps working - which means a plain type whitelist containing
``ConnectionError`` would retry every blocked request, the single worst thing
this policy exists to prevent. ``NEVER_RETRY`` is therefore consulted first.
"""

from typing import Callable

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from vnstock.config import Config
from vnstock.core.exceptions import DataSourceBlockedError, NetworkError

__all__ = [
    "NEVER_RETRY",
    "RETRYABLE_EXCEPTIONS",
    "TRANSIENT",
    "api_retry",
    "network_retry",
    "should_retry",
]

# Failures that never heal on their own. DataSourceBlockedError must sit here
# and must be tested FIRST - see the module docstring.
NEVER_RETRY: tuple[type[BaseException], ...] = (
    DataSourceBlockedError,
    ValueError,
    TypeError,
    KeyError,
    NotImplementedError,
)

# Genuinely momentary failures, where trying again is reasonable.
# NetworkError covers the library's own TimeoutError.
TRANSIENT: tuple[type[BaseException], ...] = (
    ConnectionError,
    TimeoutError,
    OSError,
    NetworkError,
)


def should_retry(exc: BaseException) -> bool:
    """Decide whether a failure is worth another attempt."""
    if isinstance(exc, NEVER_RETRY):
        return False
    return isinstance(exc, TRANSIENT)


# A ready-made decorator. Prefer this over rebuilding the policy at each call
# site: every copy is a chance for one of them to drift.
network_retry = retry(
    stop=stop_after_attempt(Config.RETRIES),
    wait=wait_exponential(
        multiplier=Config.BACKOFF_MULTIPLIER,
        min=Config.BACKOFF_MIN,
        max=Config.BACKOFF_MAX,
    ),
    retry=retry_if_exception(should_retry),
    reraise=True,
)


def api_retry(func: Callable) -> Callable:
    """Retry transient network failures, let everything else through as-is."""
    return network_retry(func)


# Deprecated alias for the old type whitelist. Kept so code that imported it
# keeps importing; prefer ``should_retry``, which also refuses the blocked
# subclasses that a bare type check silently lets through.
RETRYABLE_EXCEPTIONS = TRANSIENT
