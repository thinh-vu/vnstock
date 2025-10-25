"""
Unified provider registry system.

This module provides a centralized registry for all data providers
(both scraping-based in explorer/ and API-based in connector/).
"""

from typing import Dict, List, Optional, Type, Any, Callable
from vnstock.core.types import DataCategory, ProviderType
from vnstock.core.exceptions import (
    UnsupportedProviderError,
    ProviderInitializationError,
)


class ProviderRegistry:
    """
    Centralized registry for all data providers.

    Provides decorator-based registration and querying of providers
    across both explorer/ (scraping) and connector/ (API) folders.

    Example:
        @ProviderRegistry.register(DataCategory.QUOTE, "vci", ProviderType.SCRAPING)  # noqa: E501
        class VCIQuoteProvider(BaseProvider):
            ...

        @ProviderRegistry.register(DataCategory.QUOTE, "fmp", ProviderType.API)  # noqa: E501
        class FMPQuoteProvider(BaseProvider):
            ...

        # Query providers
        provider_cls = ProviderRegistry.get_provider("quote", "vci")
        providers = ProviderRegistry.list_providers()
    """

    # Registry structure:
    # {
    #   DataCategory.QUOTE: {
    #     "vci": {
    #       "class": VCIQuoteProvider,
    #       "type": ProviderType.SCRAPING,
    #       "name": "vci"
    #     }
    #   }
    # }
    _registry: Dict[DataCategory, Dict[str, Dict[str, Any]]] = {}

    @classmethod
    def register(
        cls,
        category: DataCategory,
        name: str,
        provider_type: ProviderType,
    ) -> Callable:
        """
        Decorator to register a provider.

        Args:
            category: Data category (QUOTE, COMPANY, etc.)
            name: Provider name (lowercase, e.g., "vci", "fmp")
            provider_type: SCRAPING or API

        Returns:
            Decorator function

        Example:
            @ProviderRegistry.register(
                DataCategory.QUOTE,
                "vci",
                ProviderType.SCRAPING
            )
            class VCIQuoteProvider(BaseProvider):
                pass
        """

        def decorator(provider_class: Type) -> Type:
            # Initialize category if not exists
            if category not in cls._registry:
                cls._registry[category] = {}

            # Check for duplicate registration
            if name in cls._registry[category]:
                existing = cls._registry[category][name]
                raise ProviderInitializationError(
                    provider=name,
                    reason=(
                        f"Provider '{name}' already registered for "
                        f"category '{category}' by class "
                        f"'{existing['class'].__name__}'"
                    ),
                )

            # Register provider
            cls._registry[category][name] = {
                "class": provider_class,
                "type": provider_type,
                "name": name,
                "category": category,
            }

            # Add metadata to provider class
            provider_class._vnstock_category = category
            provider_class._vnstock_name = name
            provider_class._vnstock_type = provider_type

            return provider_class

        return decorator

    @classmethod
    def get_provider(
        cls, category: DataCategory, name: str
    ) -> Type:
        """
        Get provider class by category and name.

        Args:
            category: Data category
            name: Provider name

        Returns:
            Provider class

        Raises:
            UnsupportedProviderError: If provider not found
        """
        # Check if category exists
        if category not in cls._registry:
            raise UnsupportedProviderError(
                provider=name,
                category=category.value,
                available_providers=list(cls.list_providers().keys()),
            )

        # Check if provider exists in category
        if name not in cls._registry[category]:
            available = list(cls._registry[category].keys())
            raise UnsupportedProviderError(
                provider=name,
                category=category.value,
                available_providers=available,
            )

        return cls._registry[category][name]["class"]

    @classmethod
    def get_provider_info(
        cls, category: DataCategory, name: str
    ) -> Dict[str, Any]:
        """
        Get full provider information.

        Args:
            category: Data category
            name: Provider name

        Returns:
            Dictionary with provider metadata

        Raises:
            UnsupportedProviderError: If provider not found
        """
        if (
            category not in cls._registry
            or name not in cls._registry[category]
        ):
            raise UnsupportedProviderError(
                provider=name, category=category.value
            )

        return cls._registry[category][name]

    @classmethod
    def list_providers(
        cls, category: Optional[DataCategory] = None
    ) -> Dict[str, Any]:
        """
        List all registered providers.

        Args:
            category: Optional category filter

        Returns:
            Dictionary structured by category and type

        Example:
            {
                "quote": {
                    "scraping": ["vci", "tcbs", "msn"],
                    "api": ["fmp", "xno"]
                },
                "company": {
                    "scraping": ["vci"],
                    "api": ["fmp"]
                }
            }
        """
        result = {}

        categories = (
            [category] if category else list(cls._registry.keys())
        )

        for cat in categories:
            if cat not in cls._registry:
                continue

            result[cat.value] = {"scraping": [], "api": []}

            for name, info in cls._registry[cat].items():
                provider_type = info["type"]
                type_key = (
                    "scraping"
                    if provider_type == ProviderType.SCRAPING
                    else "api"
                )
                result[cat.value][type_key].append(name)

        return result

    @classmethod
    def is_registered(cls, category: DataCategory, name: str) -> bool:
        """
        Check if a provider is registered.

        Args:
            category: Data category
            name: Provider name

        Returns:
            True if registered, False otherwise
        """
        return (
            category in cls._registry
            and name in cls._registry[category]
        )

    @classmethod
    def is_api_provider(cls, name: str) -> bool:
        """
        Check if a provider uses API (vs scraping).

        Args:
            name: Provider name

        Returns:
            True if API provider, False if scraping provider

        Raises:
            UnsupportedProviderError: If provider not found
        """
        # Search across all categories
        for category in cls._registry.values():
            if name in category:
                return category[name]["type"] == ProviderType.API

        # Provider not found
        raise UnsupportedProviderError(
            provider=name, available_providers=cls.get_all_provider_names()
        )

    @classmethod
    def is_scraping_provider(cls, name: str) -> bool:
        """
        Check if a provider uses scraping (vs API).

        Args:
            name: Provider name

        Returns:
            True if scraping provider, False if API provider

        Raises:
            UnsupportedProviderError: If provider not found
        """
        return not cls.is_api_provider(name)

    @classmethod
    def get_all_provider_names(cls) -> List[str]:
        """
        Get list of all provider names across all categories.

        Returns:
            List of unique provider names
        """
        names = set()
        for category in cls._registry.values():
            names.update(category.keys())
        return list(names)

    @classmethod
    def get_providers_by_type(
        cls, provider_type: ProviderType
    ) -> List[str]:
        """
        Get all providers of a specific type.

        Args:
            provider_type: SCRAPING or API

        Returns:
            List of provider names
        """
        names = []
        for category in cls._registry.values():
            for name, info in category.items():
                if info["type"] == provider_type:
                    names.append(name)
        return list(set(names))  # Remove duplicates

    @classmethod
    def clear(cls) -> None:
        """Clear all registered providers. Mainly for testing."""
        cls._registry.clear()

    @classmethod
    def get_registry_summary(cls) -> str:
        """
        Get human-readable summary of registered providers.

        Returns:
            Formatted string with registry contents
        """
        lines = ["Provider Registry Summary:", "=" * 50]

        if not cls._registry:
            lines.append("No providers registered.")
            return "\n".join(lines)

        for category, providers in cls._registry.items():
            lines.append(f"\n{category.value.upper()}:")
            for name, info in sorted(providers.items()):
                type_str = (
                    "API"
                    if info["type"] == ProviderType.API
                    else "Scraping"
                )
                lines.append(
                    f"  - {name:15s} [{type_str:8s}] "
                    f"({info['class'].__name__})"
                )

        return "\n".join(lines)
