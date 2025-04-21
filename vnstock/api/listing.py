# vnstock/api/listing.py

from typing import Any
from tenacity import retry, stop_after_attempt, wait_exponential
from vnstock.config import Config
from vnstock.base import BaseAdapter, dynamic_method

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
        source: str = "vci",
        random_agent: bool = False,
        show_log: bool = False
    ):
        # Validate the source to only accept vci or msn
        if source.lower() not in ["vci", "msn"]:
            raise ValueError("Lớp Listing chỉ nhận giá trị tham số source là 'VCI' hoặc 'MSN'.")
        # BaseAdapter will discover vnstock.explorer.<real_source>.listing
        # and pass only the kwargs its __init__ accepts (random_agent, show_log).
        super().__init__(
            source=source,
            random_agent=random_agent,
            show_log=show_log
        )

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
