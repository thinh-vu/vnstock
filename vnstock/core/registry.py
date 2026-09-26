"""
Provider Registry System for vnstock.

Providers (VCI, TCBS, MSN, FMP, XNO and so on) register themselves here to become
available data sources.

The registry lets you:
- register a provider from any package (explorer/, connector/, ...)
- look one up by provider type and source name
- list everything currently available
"""

from logging import getLogger
from typing import Dict, List, Optional, Tuple, Type

logger = getLogger(__name__)


class ProviderRegistry:
    """
    Registry for vnstock data providers.

    Accepts provider classes from either package:
    - vnstock.explorer.* (VCI, MSN, KBS, ...) - public web endpoints
    - vnstock.connector.* (FMP, XNO, Binance, ...) - REST API partners
    """

    # Registry structure: {(provider_type, source_name_lower): provider_class}
    _registry: Dict[Tuple[str, str], Type] = {}

    @classmethod
    def register(
        cls, provider_type: str, source_name: str, provider_class: Type
    ) -> None:
        """
        Register a provider class.

        Args:
            provider_type (str): Provider type
                                 (quote, company, financial, etc.)
            source_name (str): Data source name
                              (vci, fmp, tcbs, msn, kbs, etc.)
            provider_class (Type): The provider class

        Examples:
            ProviderRegistry.register('quote', 'fmp', FMPQuote)
            ProviderRegistry.register('quote', 'vci', VCIQuote)
            ProviderRegistry.register('quote', 'kbs', KBSQuote)
        """
        key = (provider_type, source_name.lower())
        cls._registry[key] = provider_class
        logger.debug(
            f"✓ Provider registered: {provider_type}/{source_name} "
            f"-> {provider_class.__module__}.{provider_class.__name__}"
        )

    @classmethod
    def get(cls, provider_type: str, source_name: str) -> Optional[Type]:
        """
        Get a provider class by type and source name.

        Args:
            provider_type (str): Provider type (quote, company, etc.)
            source_name (str): Data source name

        Returns:
            Type: The provider class

        Raises:
            ValueError: If no provider is registered under that type and source
        """
        key = (provider_type, source_name.lower())

        if key not in cls._registry:
            available = cls.list_available(provider_type)
            raise ValueError(
                f"Provider '{provider_type}/{source_name}' not found. "
                f"Available: {available}"
            )

        return cls._registry[key]

    @classmethod
    def list_available(cls, provider_type: str) -> List[str]:
        """
        List every source name available for one provider type.

        Args:
            provider_type (str): Provider type

        Returns:
            List[str]: Source names, sorted
        """
        names = sorted(
            {source for ptype, source in cls._registry if ptype == provider_type}
        )
        return names

    @classmethod
    def list_all(cls) -> Dict[str, List[str]]:
        """
        List every registered provider, grouped by type.

        Returns:
            Dict[str, List[str]]: {provider_type: [source_names]}
        """
        result = {}
        for ptype, source in cls._registry:
            if ptype not in result:
                result[ptype] = []
            result[ptype].append(source)

        # Sort the sources within each type
        for ptype in result:
            result[ptype].sort()

        return result

    @classmethod
    def is_registered(cls, provider_type: str, source_name: str) -> bool:
        """
        Check whether a provider is registered.

        Args:
            provider_type (str): Provider type
            source_name (str): Data source name

        Returns:
            bool: True when the provider is registered
        """
        key = (provider_type, source_name.lower())
        return key in cls._registry

    @classmethod
    def clear(cls) -> None:
        """
        Clear every registered provider. Mainly for tests.
        """
        cls._registry.clear()
        logger.debug("Registry cleared")

    @classmethod
    def debug_info(cls) -> str:
        """
        Return a readable dump of the registry state.

        Returns:
            str: Debug info
        """
        info = []
        info.append("=" * 60)
        info.append("PROVIDER REGISTRY DEBUG INFO")
        info.append("=" * 60)

        all_providers = cls.list_all()
        if not all_providers:
            info.append("(Registry empty)")
        else:
            for provider_type in sorted(all_providers.keys()):
                sources = all_providers[provider_type]
                info.append(f"\n[{provider_type}]")
                for source in sources:
                    provider_class = cls.get(provider_type, source)
                    info.append(
                        f"  • {source:12} -> "
                        f"{provider_class.__module__}.{provider_class.__name__}"
                    )

        info.append("\n" + "=" * 60)
        return "\n".join(info)
