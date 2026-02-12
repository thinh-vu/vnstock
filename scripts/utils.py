"""
Shared utilities for data collection scripts.

Provides:
- API key registration
- Rate limiter to avoid exceeding API limits

Rate limit auto-detection:
    1. VNSTOCK_RATE_LIMIT env var (highest priority, override)
    2. vnai.check_api_key_status() (auto-detect from API key)
    3. Default: 60 req/min (Community tier)

Environment variables:
    VNSTOCK_API_KEY       - API key for vnstock authentication
    VNSTOCK_RATE_LIMIT    - Override rate limit (e.g. 500 for Golden tier)
"""

import os
import time
import logging

logger = logging.getLogger("utils")

# ============================================================
# API KEY REGISTRATION
# ============================================================

def register_api_key():
    """
    Register vnstock API key from environment variable VNSTOCK_API_KEY.
    Must be called at the start of each script.
    Returns the detected rate limit (requests per minute).

    Priority:
        1. VNSTOCK_RATE_LIMIT env var (manual override)
        2. vnai tier detection
        3. Default: 60 req/min
    """
    # Check for manual override first
    rate_limit_override = os.environ.get("VNSTOCK_RATE_LIMIT", "")
    if rate_limit_override:
        try:
            rate_limit = int(rate_limit_override)
            logger.info(f"Rate limit override: {rate_limit} req/min (from VNSTOCK_RATE_LIMIT)")
            return rate_limit
        except ValueError:
            logger.warning(f"Invalid VNSTOCK_RATE_LIMIT: {rate_limit_override}")

    api_key = os.environ.get("VNSTOCK_API_KEY", "")
    rate_limit = 60  # Default: Community tier

    if not api_key:
        logger.warning("VNSTOCK_API_KEY not set. Using Community tier (60 req/min).")
        return rate_limit

    try:
        from vnai import setup_api_key, check_api_key_status

        setup_api_key(api_key)

        status = check_api_key_status()
        if status and status.get("has_api_key"):
            tier = status.get("tier", "community")
            limits = status.get("limits", {})
            rate_limit = limits.get("per_minute", 60)
            logger.info(f"API key registered. Tier: {tier}, Limit: {rate_limit} req/min")
        else:
            logger.info("API key registered. Tier: Community (60 req/min)")

    except Exception as e:
        logger.warning(f"Failed to register API key: {e}")

    return rate_limit


# ============================================================
# RATE LIMITER
# ============================================================

class RateLimiter:
    """
    Simple rate limiter that tracks request count per minute window.
    Automatically pauses when approaching the limit.

    Usage:
        limiter = RateLimiter(requests_per_minute=60)
        for symbol in symbols:
            limiter.wait()  # Call before each API request
            data = api_call(symbol)
    """

    def __init__(self, requests_per_minute: int = 60, safety_margin: float = 0.85):
        """
        Args:
            requests_per_minute: Max requests allowed per minute.
            safety_margin: Use only this fraction of the limit (0.85 = 85%).
        """
        self.rpm = requests_per_minute
        self.safe_rpm = int(requests_per_minute * safety_margin)
        self.min_interval = 60.0 / self.safe_rpm  # seconds between requests
        self._last_request_time = 0.0
        self._request_count = 0
        self._window_start = time.time()

    def wait(self):
        """Wait if necessary to stay within rate limit."""
        now = time.time()

        # Reset window every 60 seconds
        elapsed = now - self._window_start
        if elapsed >= 60.0:
            self._request_count = 0
            self._window_start = now

        # If we've hit the safe limit within the current window, wait for window reset
        if self._request_count >= self.safe_rpm:
            wait_time = 60.0 - elapsed + 1.0  # +1s buffer
            if wait_time > 0:
                logger.info(f"Rate limit: {self._request_count}/{self.rpm} req/min. Waiting {wait_time:.0f}s...")
                time.sleep(wait_time)
            self._request_count = 0
            self._window_start = time.time()

        # Enforce minimum interval between requests
        since_last = time.time() - self._last_request_time
        if since_last < self.min_interval:
            time.sleep(self.min_interval - since_last)

        self._last_request_time = time.time()
        self._request_count += 1

    @property
    def delay(self):
        """Minimum delay between requests in seconds."""
        return self.min_interval


# Global rate limiter instance (initialized by init_rate_limiter)
_global_limiter = None


def init_rate_limiter(requests_per_minute: int = None):
    """
    Initialize global rate limiter. Call after register_api_key().

    Args:
        requests_per_minute: Override rate limit. If None, auto-detect from API key.
    """
    global _global_limiter

    if requests_per_minute is None:
        requests_per_minute = register_api_key()

    _global_limiter = RateLimiter(requests_per_minute=requests_per_minute)
    logger.info(f"Rate limiter: {requests_per_minute} req/min → {_global_limiter.min_interval:.2f}s/req")
    return _global_limiter


def get_limiter() -> RateLimiter:
    """Get the global rate limiter. Initialize if needed."""
    global _global_limiter
    if _global_limiter is None:
        return init_rate_limiter()
    return _global_limiter
