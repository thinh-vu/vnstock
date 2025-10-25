"""
Base provider class for all data providers.

This module provides the base class that all providers (both
scraping and API-based) should inherit from.
"""

from typing import Optional, Dict, Any
from abc import ABC
from vnstock.core.settings import get_config
from vnstock.core.types import DataCategory, ProviderType
from vnstock.core.exceptions import (
    MissingAPIKeyError,
    ConfigurationError,
)


class BaseProvider(ABC):
    """
    Base class for all data providers.

    Provides common functionality:
    - API key loading from config
    - Symbol management
    - Provider metadata tracking
    - Common initialization

    Attributes:
        _vnstock_category: Data category (set by registry decorator)
        _vnstock_name: Provider name (set by registry decorator)
        _vnstock_type: Provider type (set by registry decorator)
    """

    # Metadata - set by registry decorator
    _vnstock_category: Optional[DataCategory] = None
    _vnstock_name: Optional[str] = None
    _vnstock_type: Optional[ProviderType] = None

    def __init__(
        self,
        symbol: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize base provider.

        Args:
            symbol: Stock symbol (optional)
            api_key: API key (optional, loads from config if not provided)
            **kwargs: Additional provider-specific parameters
        """
        self.symbol = symbol
        self._kwargs = kwargs

        # Load API key for API providers
        if self._vnstock_type == ProviderType.API:
            self.api_key = self._load_api_key(api_key)
        else:
            self.api_key = None

    def _load_api_key(self, provided_key: Optional[str]) -> str:
        """
        Load API key from provided argument or config.

        Args:
            provided_key: API key provided by user

        Returns:
            API key string

        Raises:
            MissingAPIKeyError: If key not provided and not in config
        """
        # Use provided key if available
        if provided_key:
            return provided_key

        # Try loading from config
        config = get_config()
        config_key = config.get_api_key(self._vnstock_name or "")

        if config_key:
            return config_key

        # Key not found - raise error
        env_var = f"VNSTOCK_{(self._vnstock_name or '').upper()}_API_KEY"
        raise MissingAPIKeyError(
            provider=self._vnstock_name or "unknown", env_var=env_var
        )

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return self._vnstock_name or self.__class__.__name__

    @property
    def provider_type(self) -> Optional[ProviderType]:
        """Get provider type (SCRAPING or API)."""
        return self._vnstock_type

    @property
    def provider_category(self) -> Optional[DataCategory]:
        """Get provider category."""
        return self._vnstock_category

    @property
    def is_api_provider(self) -> bool:
        """Check if this is an API provider."""
        return self._vnstock_type == ProviderType.API

    @property
    def is_scraping_provider(self) -> bool:
        """Check if this is a scraping provider."""
        return self._vnstock_type == ProviderType.SCRAPING

    def set_symbol(self, symbol: str) -> None:
        """
        Set or update symbol.

        Args:
            symbol: Stock symbol
        """
        self.symbol = symbol

    def get_info(self) -> Dict[str, Any]:
        """
        Get provider information.

        Returns:
            Dictionary with provider metadata
        """
        return {
            "name": self.provider_name,
            "type": self.provider_type.value if self.provider_type else None,
            "category": (
                self.provider_category.value
                if self.provider_category
                else None
            ),
            "class": self.__class__.__name__,
            "symbol": self.symbol,
            "has_api_key": bool(self.api_key),
        }

    def __repr__(self) -> str:
        """String representation."""
        parts = [self.__class__.__name__]
        if self.symbol:
            parts.append(f"symbol={self.symbol}")
        if self._vnstock_name:
            parts.append(f"provider={self._vnstock_name}")
        return f"<{' '.join(parts)}>"

    def __str__(self) -> str:
        """Human-readable string."""
        return self.__repr__()


class QuoteProviderMixin:
    """Mixin for quote data providers."""

    def _validate_date_range(self, start: str, end: str) -> None:
        """
        Validate date range parameters.

        Args:
            start: Start date
            end: End date

        Raises:
            ConfigurationError: If dates are invalid
        """
        from datetime import datetime

        try:
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d")

            if start_dt > end_dt:
                raise ConfigurationError(
                    "Start date cannot be after end date",
                    config_key="date_range",
                    details={"start": start, "end": end},
                )
        except ValueError as e:
            raise ConfigurationError(
                f"Invalid date format: {e}. Use YYYY-MM-DD",
                config_key="date_format",
            )


class CompanyProviderMixin:
    """Mixin for company data providers."""

    def _validate_symbol(self, symbol: Optional[str] = None) -> str:
        """
        Validate and return symbol.

        Args:
            symbol: Symbol to validate (uses self.symbol if None)

        Returns:
            Validated symbol

        Raises:
            ConfigurationError: If symbol is missing or invalid
        """
        # Use provided symbol or instance symbol
        sym = symbol or getattr(self, "symbol", None)

        if not sym:
            raise ConfigurationError(
                "Symbol is required",
                config_key="symbol",
                details={"provider": getattr(self, "_vnstock_name", None)},
            )

        # Basic validation
        sym = sym.strip().upper()
        if not sym:
            raise ConfigurationError(
                "Symbol cannot be empty", config_key="symbol"
            )

        return sym


class FinancialProviderMixin:
    """Mixin for financial data providers."""

    def _validate_period(self, period: str) -> str:
        """
        Validate period parameter.

        Args:
            period: Period string ('quarter' or 'year')

        Returns:
            Validated period

        Raises:
            ConfigurationError: If period is invalid
        """
        valid_periods = ["quarter", "year"]
        period = period.lower()

        if period not in valid_periods:
            raise ConfigurationError(
                f"Invalid period: {period}",
                config_key="period",
                details={"valid_periods": valid_periods},
            )

        return period
