"""
Configuration management for vnstock library.

This module provides centralized configuration with environment
variable support using dataclasses.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class APIKeyConfig:
    """API keys for various providers."""

    fmp: Optional[str] = None
    xno: Optional[str] = None
    binance: Optional[str] = None
    dnse: Optional[str] = None

    def get(self, provider: str) -> Optional[str]:
        """
        Get API key for a specific provider.

        Args:
            provider: Provider name (lowercase)

        Returns:
            API key string or None if not set
        """
        return getattr(self, provider.lower(), None)

    def set(self, provider: str, api_key: str) -> None:
        """
        Set API key for a specific provider.

        Args:
            provider: Provider name (lowercase)
            api_key: API key string
        """
        setattr(self, provider.lower(), api_key)


@dataclass
class NetworkConfig:
    """Network and HTTP request configuration."""

    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    user_agent: str = "vnstock/3.0"

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.timeout > 300:
            raise ValueError("timeout cannot exceed 300 seconds")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")


@dataclass
class CacheConfig:
    """Caching configuration."""

    enabled: bool = False
    ttl: int = 300  # seconds
    max_size: int = 100

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.ttl < 0:
            raise ValueError("ttl must be non-negative")
        if self.max_size <= 0:
            raise ValueError("max_size must be positive")


@dataclass
class VnstockConfig:
    """
    Main configuration class for vnstock.

    Supports loading from:
    1. Environment variables (VNSTOCK_* prefix)
    2. Direct instantiation

    Example:
        # From environment variables
        export VNSTOCK_FMP_API_KEY="your_key"
        export VNSTOCK_TIMEOUT=60

        # Or in code
        config = VnstockConfig(
            api_keys=APIKeyConfig(fmp="your_key"),
            network=NetworkConfig(timeout=60)
        )
    """

    api_keys: APIKeyConfig = field(default_factory=APIKeyConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    log_level: str = "INFO"
    debug_mode: bool = False
    default_source: str = "tcbs"

    def __post_init__(self):
        """Validate and load from environment after initialization."""
        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_levels:
            raise ValueError(
                f"Invalid log level: {self.log_level}. "
                f"Must be one of: {', '.join(valid_levels)}"
            )
        self.log_level = self.log_level.upper()

        # Load from environment if not set
        self._load_from_env()

    def _load_from_env(self):
        """Load configuration from environment variables."""
        # API Keys
        if os.getenv("VNSTOCK_FMP_API_KEY") and not self.api_keys.fmp:
            self.api_keys.fmp = os.getenv("VNSTOCK_FMP_API_KEY")
        if os.getenv("VNSTOCK_XNO_API_KEY") and not self.api_keys.xno:
            self.api_keys.xno = os.getenv("VNSTOCK_XNO_API_KEY")
        if os.getenv("VNSTOCK_BINANCE_API_KEY") and not self.api_keys.binance:
            self.api_keys.binance = os.getenv("VNSTOCK_BINANCE_API_KEY")
        if os.getenv("VNSTOCK_DNSE_API_KEY") and not self.api_keys.dnse:
            self.api_keys.dnse = os.getenv("VNSTOCK_DNSE_API_KEY")

        # Network config
        timeout_env = os.getenv("VNSTOCK_TIMEOUT")
        if timeout_env:
            try:
                self.network.timeout = float(timeout_env)
            except (ValueError, TypeError):
                pass

        max_retries_env = os.getenv("VNSTOCK_MAX_RETRIES")
        if max_retries_env:
            try:
                self.network.max_retries = int(max_retries_env)
            except (ValueError, TypeError):
                pass

        # Other settings
        log_level_env = os.getenv("VNSTOCK_LOG_LEVEL")
        if log_level_env:
            self.log_level = log_level_env.upper()

        debug_mode_env = os.getenv("VNSTOCK_DEBUG_MODE")
        if debug_mode_env:
            debug_value = debug_mode_env.lower()
            self.debug_mode = debug_value in ("true", "1", "yes")

        default_source_env = os.getenv("VNSTOCK_DEFAULT_SOURCE")
        if default_source_env:
            self.default_source = default_source_env

    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Get API key for a provider.

        Args:
            provider: Provider name

        Returns:
            API key or None
        """
        return self.api_keys.get(provider)

    def set_api_key(self, provider: str, api_key: str) -> None:
        """
        Set API key for a provider.

        Args:
            provider: Provider name
            api_key: API key string
        """
        self.api_keys.set(provider, api_key)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert config to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "api_keys": {
                "fmp": self.api_keys.fmp,
                "xno": self.api_keys.xno,
                "binance": self.api_keys.binance,
                "dnse": self.api_keys.dnse,
            },
            "network": {
                "timeout": self.network.timeout,
                "max_retries": self.network.max_retries,
                "retry_delay": self.network.retry_delay,
                "user_agent": self.network.user_agent,
            },
            "cache": {
                "enabled": self.cache.enabled,
                "ttl": self.cache.ttl,
                "max_size": self.cache.max_size,
            },
            "log_level": self.log_level,
            "debug_mode": self.debug_mode,
            "default_source": self.default_source,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VnstockConfig":
        """
        Create config from dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            VnstockConfig instance
        """
        api_keys = APIKeyConfig(**data.get("api_keys", {}))
        network = NetworkConfig(**data.get("network", {}))
        cache = CacheConfig(**data.get("cache", {}))

        return cls(
            api_keys=api_keys,
            network=network,
            cache=cache,
            log_level=data.get("log_level", "INFO"),
            debug_mode=data.get("debug_mode", False),
            default_source=data.get("default_source", "tcbs"),
        )


# ============================================================================
# GLOBAL CONFIG INSTANCE
# ============================================================================

# Global config instance - can be modified by users
_global_config: Optional[VnstockConfig] = None


def get_config() -> VnstockConfig:
    """
    Get global config instance.

    Creates default config if not already initialized.

    Returns:
        VnstockConfig instance
    """
    global _global_config
    if _global_config is None:
        _global_config = VnstockConfig()
    return _global_config


def set_config(config: VnstockConfig) -> None:
    """
    Set global config instance.

    Args:
        config: VnstockConfig instance
    """
    global _global_config
    _global_config = config


def reset_config() -> None:
    """Reset global config to default values."""
    global _global_config
    _global_config = VnstockConfig()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_api_key(provider: str) -> Optional[str]:
    """
    Get API key for a provider from global config.

    Args:
        provider: Provider name

    Returns:
        API key or None
    """
    config = get_config()
    return config.get_api_key(provider)


def set_api_key(provider: str, api_key: str) -> None:
    """
    Set API key for a provider in global config.

    Args:
        provider: Provider name
        api_key: API key string
    """
    config = get_config()
    config.set_api_key(provider, api_key)


def get_timeout() -> float:
    """Get default timeout from global config."""
    config = get_config()
    return config.network.timeout


def set_timeout(timeout: float) -> None:
    """
    Set default timeout in global config.

    Args:
        timeout: Timeout in seconds
    """
    config = get_config()
    config.network.timeout = timeout


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    config = get_config()
    return config.debug_mode


def set_debug_mode(enabled: bool) -> None:
    """
    Enable or disable debug mode.

    Args:
        enabled: True to enable, False to disable
    """
    config = get_config()
    config.debug_mode = enabled
