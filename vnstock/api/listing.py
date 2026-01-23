# vnstock/api/listing.py

from typing import Any, Optional
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_exponential
from vnstock.config import Config
from vnstock.base import BaseAdapter, dynamic_method


def source_required(func):
    """Decorator to ensure source is specified for source-specific methods.
    
    This decorator is applied BEFORE @retry so that ValueError from missing source
    is raised immediately without retry logic.
    """
    method_name = func.__name__

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Check provider before any retry logic
        if self.provider is None:
            raise ValueError(
                f"Method '{method_name}()' requires a data source. "
                f"Initialize with Listing(source='vci'|'kbs'|'msn') "
                f"or use source-independent methods like all_indices(), indices_by_group()."
            )
        return func(self, *args, **kwargs)

    return wrapper


class Listing(BaseAdapter):
    _module_name = "listing"
    """
    Adapter for listing data:
      - all_symbols
      - symbols_by_industries
      - symbols_by_exchange
      - industries_icb
      - symbols_by_group
      - all_future_indices
      - all_government_bonds
      - all_covered_warrant
      - all_bonds

    Usage:
        lst = Listing(source="vci", random_agent=False, show_log=True)
        df = lst.all_symbols(to_df=True)
        df2 = lst.symbols_by_exchange(lang="en")
        idx = lst.industries_icb()
        group = lst.symbols_by_group(group="VN30")
        fu = lst.all_future_indices()
    """
    def __init__(
        self,
        source: str = None,
        random_agent: bool = False,
        show_log: bool = False
    ):
        # Ensure explorer modules are loaded (lazy load to avoid deadlock)
        from vnstock import _ensure_explorer_modules_loaded
        _ensure_explorer_modules_loaded()
        
        # Store parameters for later use
        self.source = source
        self.random_agent = random_agent
        self.show_log = show_log
        
        # Validate the source if provided
        if source is not None and source.lower() not in ["kbs", "vci", "msn"]:
            raise ValueError("Lớp Listing chỉ nhận giá trị tham số source là 'KBS', 'VCI' hoặc 'MSN'.")
        
        # BaseAdapter will discover vnstock.explorer.<real_source>.listing
        # and pass only the kwargs its __init__ accepts (random_agent, show_log).
        if source is not None:
            super().__init__(
                source=source,
                random_agent=random_agent,
                show_log=show_log
            )

    @source_required
    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    @dynamic_method
    def all_symbols(self, *args: Any, **kwargs: Any) -> Any:
        """Retrieve all symbols (filtered to STOCK)."""
        pass

    @source_required
    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    @dynamic_method
    def symbols_by_industries(self, *args: Any, **kwargs: Any) -> Any:
        """Retrieve symbols grouped by ICB industries."""
        pass

    @source_required
    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    @dynamic_method
    def symbols_by_exchange(self, *args: Any, **kwargs: Any) -> Any:
        """Retrieve symbols by exchange/board."""
        pass

    @source_required
    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    @dynamic_method
    def industries_icb(self, *args: Any, **kwargs: Any) -> Any:
        """Retrieve ICB code hierarchy and mapping."""
        pass

    @source_required
    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    @dynamic_method
    def symbols_by_group(self, *args: Any, **kwargs: Any) -> Any:
        """Retrieve symbols by predefined group (VN30, HNX30, CW, etc.)."""
        pass

    # shortcuts that delegate to symbols_by_group
    @source_required
    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    def all_future_indices(self, **kwargs: Any) -> Any:
        """Retrieve all futures indices (group='FU_INDEX')."""
        return self.symbols_by_group(group="FU_INDEX", **kwargs)

    @source_required
    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    def all_government_bonds(self, **kwargs: Any) -> Any:
        """Retrieve all government bonds (group='FU_BOND')."""
        return self.symbols_by_group(group="FU_BOND", **kwargs)

    @source_required
    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    def all_covered_warrant(self, **kwargs: Any) -> Any:
        """Retrieve all covered warrants (group='CW')."""
        return self.symbols_by_group(group="CW", **kwargs)

    @source_required
    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    def all_bonds(self, **kwargs: Any) -> Any:
        """Retrieve all bonds (group='BOND')."""
        return self.symbols_by_group(group="BOND", **kwargs)

    # =========================================================================
    # STANDARDIZED MARKET INDICES (Wrapper functions)
    # =========================================================================
    # Provide access to standardized indices across all data sources
    # (VCI, KBS, MSN, etc.). Sector indices include mapping to ICB
    # sector_id for industry filtering and analysis.

    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    def all_indices(self) -> Any:
        """
        Lấy danh sách tất cả các chỉ số tiêu chuẩn hóa với thông tin đầy đủ.

        Returns:
            pd.DataFrame: Columns [symbol, name, description, full_name,
                                   group, index_id, sector_id (for sectors)]
        """
        from vnstock.common import indices as market_indices
        return market_indices.get_all_indices()

    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    def indices_by_group(self, group: str) -> Optional[Any]:
        """
        Lấy danh sách chỉ số theo nhóm tiêu chuẩn hóa.

        Args:
            group: Tên nhóm (VD: 'HOSE Indices', 'Sector Indices', etc.)

        Returns:
            pd.DataFrame: Danh sách chỉ số trong nhóm hoặc None
                          (Sector indices include sector_id mapping)
        """
        from vnstock.common import indices as market_indices
        return market_indices.get_indices_by_group(group)
        
    def _delegate_to_provider(self, method_name: str, **kwargs: Any) -> Any:
        """
        Delegate method call to the provider.

        Args:
            method_name (str): Method name to call.
            **kwargs: Additional parameters.

        Returns:
            Any: Result from the provider.
        """
        # Standard vnstock implementation
        method = getattr(self.provider, method_name)
        return method(**kwargs)
