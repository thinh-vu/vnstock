"""
Custom exceptions for vnstock library.

This module provides a hierarchy of exceptions with error codes
for better error handling and debugging.
"""

from typing import Any, Dict, Optional

# ============================================================================
# BASE EXCEPTION
# ============================================================================


class VnstockError(Exception):
    """Base exception for all vnstock errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize VnstockError.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code (e.g., 'PROVIDER_001')
            details: Additional error details
        """
        self.message = message
        self.error_code = error_code or "VNSTOCK_000"
        self.details = details or {}
        super().__init__(self.format_message())

    def format_message(self) -> str:
        """Format error message with code and details."""
        msg = f"[{self.error_code}] {self.message}"
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            msg += f" ({details_str})"
        return msg

    def __str__(self) -> str:
        return self.format_message()

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/debugging."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "type": self.__class__.__name__,
        }


# ============================================================================
# PROVIDER ERRORS
# ============================================================================


class ProviderError(VnstockError):
    """Base exception for provider-related errors."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize ProviderError.

        Args:
            message: Human-readable error message
            provider: Provider name (e.g., 'vci', 'fmp')
            error_code: Error code
            details: Additional error details
        """
        details = details or {}
        if provider:
            details["provider"] = provider

        super().__init__(
            message=message,
            error_code=error_code or "PROVIDER_000",
            details=details,
        )


class UnsupportedProviderError(ProviderError):
    """Raised when a provider is not supported or not found."""

    def __init__(
        self,
        provider: str,
        category: Optional[str] = None,
        available_providers: Optional[list] = None,
    ):
        """
        Initialize UnsupportedProviderError.

        Args:
            provider: The unsupported provider name
            category: Data category (quote, company, etc.)
            available_providers: List of available providers
        """
        msg = f"Provider '{provider}' is not supported"
        if category:
            msg += f" for category '{category}'"

        details = {}
        if available_providers:
            details["available_providers"] = available_providers

        super().__init__(
            message=msg,
            provider=provider,
            error_code="PROVIDER_001",
            details=details,
        )


class UnsupportedMethodError(ProviderError):
    """Raised when a method is not supported by the provider."""

    def __init__(
        self,
        provider: str,
        method: str,
        supported_methods: Optional[list] = None,
    ):
        """
        Initialize UnsupportedMethodError.

        Args:
            provider: Provider name
            method: The unsupported method name
            supported_methods: List of supported methods
        """
        msg = f"Method '{method}' is not supported by provider '{provider}'"

        details = {}
        if supported_methods:
            details["supported_methods"] = supported_methods

        super().__init__(
            message=msg,
            provider=provider,
            error_code="PROVIDER_002",
            details=details,
        )


class ProviderInitializationError(ProviderError):
    """Raised when provider initialization fails."""

    def __init__(
        self,
        provider: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize ProviderInitializationError.

        Args:
            provider: Provider name
            reason: Reason for initialization failure
            details: Additional error details
        """
        msg = f"Failed to initialize provider '{provider}': {reason}"

        super().__init__(
            message=msg,
            provider=provider,
            error_code="PROVIDER_003",
            details=details,
        )


# ============================================================================
# DATA ERRORS
# ============================================================================


class DataFetchError(VnstockError):
    """Raised when data fetching fails."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        symbol: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize DataFetchError.

        Args:
            message: Error message
            provider: Provider name
            symbol: Stock symbol
            status_code: HTTP status code (if applicable)
            details: Additional error details
        """
        details = details or {}
        if provider:
            details["provider"] = provider
        if symbol:
            details["symbol"] = symbol
        if status_code:
            details["status_code"] = status_code

        super().__init__(
            message=message,
            error_code="DATA_001",
            details=details,
        )


class DataParsingError(VnstockError):
    """Raised when data parsing/transformation fails."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        raw_data: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize DataParsingError.

        Args:
            message: Error message
            provider: Provider name
            raw_data: Raw data that failed to parse
            details: Additional error details
        """
        details = details or {}
        if provider:
            details["provider"] = provider
        if raw_data and len(str(raw_data)) < 200:  # Only include if small
            details["raw_data_preview"] = str(raw_data)[:200]

        super().__init__(
            message=message,
            error_code="DATA_002",
            details=details,
        )


class DataValidationError(VnstockError):
    """Raised when data validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize DataValidationError.

        Args:
            message: Error message
            field: Field name that failed validation
            value: Invalid value
            details: Additional error details
        """
        details = details or {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value

        super().__init__(
            message=message,
            error_code="DATA_003",
            details=details,
        )


# ============================================================================
# CONFIGURATION ERRORS
# ============================================================================


class ConfigurationError(VnstockError):
    """Raised when configuration is invalid or missing."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize ConfigurationError.

        Args:
            message: Error message
            config_key: Configuration key that is invalid
            details: Additional error details
        """
        details = details or {}
        if config_key:
            details["config_key"] = config_key

        super().__init__(
            message=message,
            error_code="CONFIG_001",
            details=details,
        )


class MissingAPIKeyError(ConfigurationError):
    """Raised when required API key is missing."""

    def __init__(
        self,
        provider: str,
        env_var: Optional[str] = None,
    ):
        """
        Initialize MissingAPIKeyError.

        Args:
            provider: Provider name that requires API key
            env_var: Environment variable name for the API key
        """
        msg = f"API key required for provider '{provider}'"
        if env_var:
            msg += f". Set environment variable '{env_var}' or pass api_key"

        details = {"provider": provider}
        if env_var:
            details["env_var"] = env_var

        super().__init__(
            message=msg,
            config_key="api_key",
            details=details,
        )


# ============================================================================
# NETWORK ERRORS
# ============================================================================


class NetworkError(VnstockError):
    """Raised when network request fails."""

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize NetworkError.

        Args:
            message: Error message
            url: URL that failed
            status_code: HTTP status code
            details: Additional error details
        """
        details = details or {}
        if url:
            details["url"] = url
        if status_code:
            details["status_code"] = status_code

        super().__init__(
            message=message,
            error_code="NETWORK_001",
            details=details,
        )


class TimeoutError(NetworkError):
    """Raised when request times out."""

    def __init__(
        self,
        provider: str,
        timeout: float,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize TimeoutError.

        Args:
            provider: Provider name
            timeout: Timeout value in seconds
            details: Additional error details
        """
        msg = f"Request to '{provider}' timed out after {timeout}s"

        details = details or {}
        details["provider"] = provider
        details["timeout"] = timeout

        super().__init__(
            message=msg,
            details=details,
        )


# ============================================================================
# DATA SOURCE BLOCKING
# ============================================================================
#
# These inherit the builtin ``ConnectionError`` so that code written before the
# category existed - ``except ConnectionError`` - keeps catching them unchanged.
#
# Keeping "the source blocked us" separate from "the network hiccuped" is what
# lets the retry policy know when to back off and when to stop: retrying a
# request that was already blocked only deepens the block.


class DataSourceBlockedError(VnstockError, ConnectionError):
    """The data source, or the CDN/WAF in front of it, refused the request.

    Unlike a transient network failure, retrying straight away does not help and
    actively makes things worse.

    Inherits both bases on purpose. ``ConnectionError`` keeps every existing
    ``except ConnectionError`` working, and ``VnstockError`` honours the promise
    that it is the base of all vnstock errors - without it, code catching
    ``VnstockError`` to handle everything the library raises would silently miss
    exactly the failures that most need handling.

    Attributes:
        url: The address that was called.
        host: Hostname of that address.
        status_code: HTTP status received.
        reason: Internal code naming the marker that matched, e.g. "cf_1015".
        retry_after: Seconds the server asked us to wait, when it said so.
        vendor: Protection layer identified: "cloudflare", "akamai", "unknown"...
        cooldown: Seconds the library will stop calling this host for.
        details: Extra information for logging.
    """

    error_code = "BLOCK_000"

    def __init__(
        self,
        message: str,
        *,
        url: Optional[str] = None,
        host: Optional[str] = None,
        status_code: Optional[int] = None,
        reason: Optional[str] = None,
        retry_after: Optional[float] = None,
        vendor: Optional[str] = None,
        cooldown: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        # Call the parent first so error_code and details are set exactly once; calling
        # it later lets VnstockError.__init__ overwrite details with its default.
        super().__init__(message, error_code=self.error_code, details=details)
        self.url = url
        self.host = host
        self.status_code = status_code
        self.reason = reason
        self.retry_after = retry_after
        self.vendor = vendor
        self.cooldown = cooldown

    def to_dict(self) -> Dict[str, Any]:
        """Return a dict form for structured logging or telemetry."""
        return {
            "type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "url": self.url,
            "host": self.host,
            "status_code": self.status_code,
            "reason": self.reason,
            "retry_after": self.retry_after,
            "vendor": self.vendor,
            "cooldown": self.cooldown,
            "details": self.details,
        }


class RateLimitedError(DataSourceBlockedError):
    """Rate limited: HTTP 429, or Cloudflare code 1015."""

    error_code = "BLOCK_429"


class ChallengeRequiredError(DataSourceBlockedError):
    """The protection layer wants a browser to clear an automated check."""

    error_code = "BLOCK_CHALLENGE"


class AccessDeniedError(DataSourceBlockedError):
    """Refused at the protection layer itself, usually 403 or 451."""

    error_code = "BLOCK_DENIED"


class CircuitOpenError(DataSourceBlockedError):
    """Inside a cooldown window: stop here without opening a connection.

    Inherits DataSourceBlockedError so one ``except DataSourceBlockedError``
    catches both the real block and every short-circuited call after it.

    Attributes:
        remaining: Seconds left before this host may be called again.
    """

    error_code = "BLOCK_COOLDOWN"

    def __init__(self, message: str, *, remaining: float, **kwargs: Any):
        self.remaining = remaining
        super().__init__(message, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["remaining"] = self.remaining
        return data


# Deprecated alias. ``RateLimitError`` was declared in an earlier layout but
# never raised anywhere; it now names the class that is actually raised, so that
# ``except RateLimitError`` and ``except RateLimitedError`` cannot disagree.
RateLimitError = RateLimitedError


# ============================================================================
# DEPRECATION WARNING
# ============================================================================


class DeprecationWarning(UserWarning):
    """Warning for deprecated features."""

    pass


# ============================================================================
# ERROR CODE REFERENCE
# ============================================================================

ERROR_CODES = {
    # General
    "VNSTOCK_000": "General vnstock error",
    # Provider errors
    "PROVIDER_000": "General provider error",
    "PROVIDER_001": "Unsupported provider",
    "PROVIDER_002": "Unsupported method",
    "PROVIDER_003": "Provider initialization failed",
    # Data errors
    "DATA_001": "Data fetch failed",
    "DATA_002": "Data parsing failed",
    "DATA_003": "Data validation failed",
    # Configuration errors
    "CONFIG_001": "Configuration error",
    # Network errors
    "NETWORK_001": "Network request failed",
    "NETWORK_002": "Rate limit exceeded",
    "NETWORK_003": "Request timeout",
}


def get_error_description(error_code: str) -> str:
    """
    Get description for an error code.

    Args:
        error_code: Error code string

    Returns:
        Error description or 'Unknown error code'
    """
    return ERROR_CODES.get(error_code, "Unknown error code")
