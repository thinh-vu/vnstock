# vnstock/config.py

import logging


class Config:
    # -------------------------------------------------------------------------
    # HTTP request settings
    # -------------------------------------------------------------------------
    # Default timeout (in seconds) for any network request
    REQUEST_TIMEOUT: int = 30

    # Number of retry attempts on transient failures
    RETRIES: int = 3

    # Tenacity backoff strategy parameters
    BACKOFF_MULTIPLIER: float = 1.0
    BACKOFF_MIN: float = 2  # minimum wait between retries (seconds)
    BACKOFF_MAX: float = 10  # maximum wait between retries (seconds)

    # -------------------------------------------------------------------------
    # Block detection (CDN / WAF)
    # -------------------------------------------------------------------------
    # Master switch for recognising "the source blocked us" responses.
    BLOCK_DETECTION_ENABLED: bool = True

    # Max bytes of a response body read while sniffing for block markers.
    # CDN block pages always put their marker near the top, so reading the whole
    # body is never necessary.
    BODY_SNIFF_LIMIT: int = 8192

    # Honour a Retry-After header only when the wait is at most this long, and
    # only retry once. Anything longer stops immediately and hands the decision
    # back to the caller instead of hanging their process.
    RETRY_AFTER_MAX_WAIT: float = 30.0

    # -------------------------------------------------------------------------
    # Per-host circuit breaker
    # -------------------------------------------------------------------------
    CIRCUIT_BREAKER_ENABLED: bool = True

    # Default cooldown per kind of block signal (seconds).
    BLOCK_COOLDOWN_RATE_LIMIT: float = 60.0
    BLOCK_COOLDOWN_CHALLENGE: float = 300.0
    BLOCK_COOLDOWN_DENIED: float = 300.0

    # Clamp applied to every cooldown, including one derived from Retry-After.
    BLOCK_COOLDOWN_MIN: float = 5.0
    BLOCK_COOLDOWN_MAX: float = 900.0

    # Upper bound on tracked hosts before the breaker prunes expired entries.
    CIRCUIT_MAX_ENTRIES: int = 256

    # -------------------------------------------------------------------------
    # Caching
    # -------------------------------------------------------------------------
    # Max entries for LRU‑cached methods
    CACHE_SIZE: int = 128

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------
    # Default logging level for all vnstock modules
    LOG_LEVEL: int = logging.DEBUG

    @classmethod
    def apply_logging_config(cls):
        """
        Call once at startup to configure vnstock logging.
        """
        logging.getLogger("vnstock").setLevel(cls.LOG_LEVEL)


# =============================================================================
# VERSION-SPECIFIC DEPENDENCY REQUIREMENTS & NOTICES
# =============================================================================
# Define minimum required versions for each vnstock version
# Format: "X.Y.Z": {"package_name": "min_version", ...}
VERSION_REQUIREMENTS = {
    "3.4.0": {
        "vnai": ">=2.3.0",
        "vnii": ">=0.1.5",
        # # Core dependencies - required for vnstock to work
        # "requests": ">=2.25.0,<3.0.0",
        # "pandas": ">=1.3.0,<3.0.0",
        # "beautifulsoup4": ">=4.9.0,<5.0.0",
        # "packaging": ">=20.0",
        # # Recommended optional dependencies
        # "openpyxl": ">=3.0.0",
        # "psutil": ">=5.8.0"
    }
}

# Version-specific notices for user
VERSION_NOTICES = {
    "3.4.0": {
        "title": "vnstock 3.4.0 - Major Update",
        "release_url": "https://vnstocks.com/docs/tai-lieu/lich-su-phien-ban",
        "critical_notices": [],
        "warnings": [],
    },
}

# Python version compatibility matrix
PYTHON_VERSION_SUPPORT = {"3.4.0": ["3.10", "3.11", "3.12", "3.13", "3.14"]}
