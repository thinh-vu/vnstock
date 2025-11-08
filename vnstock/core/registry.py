"""
Provider Registry System for vnstock.

Hệ thống đăng ký cho phép các provider (VCI, TCBS, MSN, FMP, XNO, ...)
tự đăng ký để trở thành available data source.

Module này cho phép:
- Đăng ký provider từ bất kỳ thư mục (explorer/, connector/, ...)
- Tìm kiếm provider theo provider_type và source name
- Liệt kê tất cả available providers
"""

from typing import Dict, Tuple, Type, List, Optional
from logging import getLogger

logger = getLogger(__name__)


class ProviderRegistry:
    """
    Registry for vnstock data providers.
    
    Cho phép registration của các provider class từ các nguồn khác nhau:
    - vnstock.explorer.* (VCI, TCBS, MSN, ...) - Web scraping
    - vnstock.connector.* (FMP, XNO, Binance, ...) - REST API
    """
    
    # Registry structure: {(provider_type, source_name_lower): provider_class}
    _registry: Dict[Tuple[str, str], Type] = {}
    
    @classmethod
    def register(
        cls,
        provider_type: str,
        source_name: str,
        provider_class: Type
    ) -> None:
        """
        Register a provider class.

        Tham số:
            provider_type (str): Type của provider
                                 (quote, company, financial, etc.)
            source_name (str): Tên nguồn dữ liệu
                              (vci, fmp, xno, tcbs, msn, etc.)
            provider_class (Type): Class của provider
            
        Ví dụ:
            ProviderRegistry.register('quote', 'fmp', FMPQuote)
            ProviderRegistry.register('quote', 'vci', VCIQuote)
        """
        key = (provider_type, source_name.lower())
        cls._registry[key] = provider_class
        logger.debug(
            f"✓ Provider registered: {provider_type}/{source_name} "
            f"-> {provider_class.__module__}.{provider_class.__name__}"
        )
    
    @classmethod
    def get(
        cls,
        provider_type: str,
        source_name: str
    ) -> Optional[Type]:
        """
        Get a provider class by type and source name.
        
        Tham số:
            provider_type (str): Type của provider (quote, company, etc.)
            source_name (str): Tên nguồn dữ liệu
            
        Returns:
            Type: Provider class nếu được tìm thấy
            
        Raises:
            ValueError: Nếu provider không được tìm thấy
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
        List all available source names cho một provider type.
        
        Tham số:
            provider_type (str): Type của provider
            
        Returns:
            List[str]: Danh sách source names (sắp xếp)
        """
        names = sorted({
            source for ptype, source in cls._registry
            if ptype == provider_type
        })
        return names
    
    @classmethod
    def list_all(cls) -> Dict[str, List[str]]:
        """
        List tất cả registered providers, grouped by type.
        
        Returns:
            Dict[str, List[str]]: {provider_type: [source_names]}
        """
        result = {}
        for ptype, source in cls._registry:
            if ptype not in result:
                result[ptype] = []
            result[ptype].append(source)
        
        # Sort sources trong mỗi type
        for ptype in result:
            result[ptype].sort()
        
        return result
    
    @classmethod
    def is_registered(cls, provider_type: str, source_name: str) -> bool:
        """
        Check xem provider có được register không.
        
        Tham số:
            provider_type (str): Type của provider
            source_name (str): Tên nguồn dữ liệu
            
        Returns:
            bool: True nếu provider được register
        """
        key = (provider_type, source_name.lower())
        return key in cls._registry
    
    @classmethod
    def clear(cls) -> None:
        """
        Clear tất cả registered providers. Chủ yếu dùng cho testing.
        """
        cls._registry.clear()
        logger.debug("Registry cleared")
    
    @classmethod
    def debug_info(cls) -> str:
        """
        Get debug info về registry state.
        
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
