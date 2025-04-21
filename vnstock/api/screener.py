import pandas as pd
from vnstock.explorer.tcbs.screener import Screener as TCBS_Screener

class Screener:
    """
    API adapter for the TCBS stock screener.
    Supports only the 'tcbs' data source.
    """
    SUPPORTED_SOURCES = ["tcbs"]

    def __init__(self, source: str = "tcbs", random_agent: bool = False, show_log: bool = False):
        """
        Initialize the Screener adapter.

        Args:
            source: Data source identifier, must be 'tcbs'.
            random_agent: Whether to use a random User-Agent in HTTP headers.
            show_log: Whether to enable debug logging.
        """
        src = source.lower()
        if src not in self.SUPPORTED_SOURCES:
            raise ValueError(f"Unsupported source: {source}. Only 'tcbs' is supported.")
        self.source = src
        self.client = TCBS_Screener(random_agent=random_agent, show_log=show_log)

    def stock(
        self,
        params: dict = None,
        limit: int = 50,
        id: str = None,
        lang: str = "vi"
    ) -> pd.DataFrame:
        """
        Run a stock screen with given filters.

        Args:
            params: Filter parameters, e.g. {"exchangeName": "HOSE,HNX,UPCOM"}.
            limit: Number of results to return.
            id: Optional screener ID.
            lang: Language code for multi-language fields ('vi' or 'en').

        Returns:
            pd.DataFrame: Screened stock data.
        """
        # Default to all exchanges if no params provided
        if params is None:
            params = {"exchangeName": "HOSE,HNX,UPCOM"}
        # Delegate to underlying TCBS Screener
        return self.client.stock(params=params, limit=limit, id=id, lang=lang)
