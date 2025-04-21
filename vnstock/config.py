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
    BACKOFF_MIN: float = 2    # minimum wait between retries (seconds)
    BACKOFF_MAX: float = 10   # maximum wait between retries (seconds)

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
