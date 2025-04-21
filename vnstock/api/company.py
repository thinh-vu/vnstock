# vnstock/api/company.py

from typing import Any
from tenacity import retry, stop_after_attempt, wait_exponential
from vnstock.config import Config
from vnstock.base import BaseAdapter, dynamic_method

class Company(BaseAdapter):
    _module_name = "company"
    """
    Adapter for company-related data:
      - overview
      - shareholders
      - officers
      - subsidiaries
      - affiliate
      - news
      - events

    Usage:
        c = Company(source="vci", symbol="VCI", random_agent=False, show_log=True)
        df_ov = c.overview()
        df_sh = c.shareholders()
        df_of = c.officers(filter_by="all")
        df_sub = c.subsidiaries(filter_by="subsidiary")
        df_aff = c.affiliate()
        df_news = c.news()
        df_evt = c.events()
    """
    def __init__(
        self,
        source: str = "vci",
        symbol: str = None,
        random_agent: bool = False,
        show_log: bool = False
    ):
        # Validate the source to only accept vci or tcbs
        if source.lower() not in ["vci", "tcbs"]:
            raise ValueError("Lớp Company chỉ nhận giá trị tham số source là 'VCI' hoặc 'TCBS'.")
        # BaseAdapter will discover vnstock.explorer.<real_source>.company
        # and pass only the kwargs its __init__ accepts (random_agent, show_log).
        super().__init__(
            source=source,
            symbol=symbol,
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
    def overview(self, *args: Any, **kwargs: Any) -> Any:
        """Retrieve company overview data."""
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
    def shareholders(self, *args: Any, **kwargs: Any) -> Any:
        """Retrieve company shareholders data."""
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
    def officers(self, *args: Any, **kwargs: Any) -> Any:
        """
        Retrieve company officers data.
        Supports kwargs like filter_by='working'|'resigned'|'all'.
        """
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
    def subsidiaries(self, *args: Any, **kwargs: Any) -> Any:
        """
        Retrieve company subsidiaries data.
        Supports kwargs like filter_by='all'|'subsidiary'.
        """
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
    def affiliate(self, *args: Any, **kwargs: Any) -> Any:
        """Retrieve company affiliate data."""
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
    def news(self, *args: Any, **kwargs: Any) -> Any:
        """Retrieve company news."""
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
    def events(self, *args: Any, **kwargs: Any) -> Any:
        """Retrieve company events."""
        pass
