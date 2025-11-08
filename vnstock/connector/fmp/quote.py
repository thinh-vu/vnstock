"""
FMP Quote connector for vnstock.

Handles fetching and processing stock price data from FMP API.
Following VCI patterns for consistency.
"""

import pandas as pd
from typing import Optional
from vnstock.core.types import TimeFrame
from vnstock.core.utils.interval import normalize_interval
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.parser import camel_to_snake
from vnstock.core.utils.transform import resample_ohlcv
from .config import FMPConfig, make_fmp_request
from .const import _OHLCV_MAP

logger = get_logger(__name__)


class Quote:
    """
    FMP Quote data provider for vnstock.

    Provides methods to fetch stock price data including real-time quotes,
    historical EOD (End-Of-Day) prices, and intraday price movements.
    """

    def __init__(self, symbol: str, api_key: Optional[str] = None,
                 show_log: Optional[bool] = True):
        """
        Initialize Quote instance.

        Args:
            symbol (str): Stock ticker symbol
            api_key (Optional[str]): FMP API key from environment or parameter
            show_log (Optional[bool]): Whether to display logging messages.
                                      Defaults to False per vnstock standards.
        """
        self.symbol = symbol.upper()
        self.config = FMPConfig(api_key=api_key, show_log=show_log)
        self.show_log = show_log

    def short(self) -> Optional[pd.DataFrame]:
        """
        Get real-time stock quote snapshot (short format).

        Fetches quick snapshots of real-time stock quotes with current price,
        volume, and price changes for instant market insights. Uses the FMP
        quote-short endpoint for minimal data.

        Returns:
            Optional[pd.DataFrame]: DataFrame with real-time quote data
        """
        url = self.config.get_endpoint_url('quote_short', self.symbol)
        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log or False)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()
            # Convert all column names to snake_case
            df.columns = [camel_to_snake(col) for col in df.columns]

        return df

    def full(self) -> Optional[pd.DataFrame]:
        """
        Get comprehensive real-time stock quote (full format).

        Fetches up-to-the-minute prices, changes, and volume data for
        individual stocks with complete quote information. Uses the FMP
        quote endpoint for full quote data.

        Returns:
            Optional[pd.DataFrame]: DataFrame with complete quote data
        """
        url = self.config.get_endpoint_url('quote', self.symbol)
        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log or False)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()
            # Convert all column names to snake_case
            df.columns = [camel_to_snake(col) for col in df.columns]

        return df

    def history(self, start: Optional[str] = None,
                end: Optional[str] = None,
                interval: str = 'd',
                adj_type: str = 'full') -> Optional[pd.DataFrame]:
        """
        Fetch historical End-Of-Day (EOD) price data.

        Returns daily price data by default. Supports resampling to weekly
        and monthly intervals from daily data.

        For intraday data (minute/hour intervals), use intraday() method.

        Args:
            start (Optional[str]): Start date (YYYY-MM-DD format)
            end (Optional[str]): End date (YYYY-MM-DD format)
            interval (str): Time interval for aggregation.
                           Supported formats per vnstock standard:
                           - 'd', '1d', '1D': Daily (direct from API)
                           - 'w', '1w', '1W': Weekly (resampled from 1D)
                           - 'M', '1M', 'month': Monthly (resampled from 1D)
                           Defaults to 'd'
            adj_type (str): Price adjustment type
                           - 'light': Light data
                           - 'full': Full adjustment (default)
                           - 'non-split-adjusted': No split adjustment
                           - 'dividend-adjusted': Dividend adjustment only
                           Defaults to 'full'

        Returns:
            Optional[pd.DataFrame]: DataFrame with OHLCV data (time, open,
                                   high, low, close, volume)
        """
        # Normalize interval to standard format
        timeframe = normalize_interval(interval)
        
        # Only EOD intervals are supported by this method
        eod_intervals = [
            TimeFrame.DAY_1,
            TimeFrame.WEEK_1,
            TimeFrame.MONTH_1
        ]

        if timeframe not in eod_intervals:
            if self.show_log:
                logger.error(
                    f"Invalid interval: {interval}. "
                    f"history() supports only EOD: d/1d/1D, w/1w/1W, M/1M. "
                    f"Use intraday() for minute-level data."
                )
            return None

        # Fetch daily data from EOD endpoint
        url = (f"{self.config.domain}/historical-price-eod/"
               f"{adj_type}?symbol={self.symbol}&apikey="
               f"{self.config.api_key}")

        if start:
            url = f"{url}&from={start}"
        if end:
            url = f"{url}&to={end}"

        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log or False)

        if df is not None and not df.empty:
            # Normalize column names to vnstock standard
            df = self._normalize_ohlcv_columns(df)

            # Ensure date column is datetime
            if 'time' in df.columns:
                df['time'] = pd.to_datetime(df['time'])
                df = df.sort_values('time', ascending=True)

                # Resample to weekly or monthly if needed
                if timeframe in [TimeFrame.WEEK_1, TimeFrame.MONTH_1]:
                    df = resample_ohlcv(df, timeframe.value)

                df = df.reset_index(drop=True)

        return df

    def intraday(self, interval: str = 'm',
                 start: Optional[str] = None,
                 end: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Fetch intraday (minute/hour level) price data.

        Retrieves precise intraday stock price and volume data with intervals
        from 1-minute to 4-hour. Returns real-time or historical stock data
        including open, high, low, close prices and trading volume.

        For End-Of-Day (daily/weekly/monthly) data, use history() method.

        Args:
            interval (str): Time interval for data aggregation.
                           Supported formats per vnstock standard:
                           - 'm', '1m': 1 minute (default)
                           - '5m': 5 minutes
                           - '15m': 15 minutes
                           - '30m': 30 minutes
                           - 'h', '1h': 1 hour
                           - '4h': 4 hours
            start (Optional[str]): Start date (YYYY-MM-DD format)
            end (Optional[str]): End date (YYYY-MM-DD format)

        Returns:
            Optional[pd.DataFrame]: DataFrame with intraday OHLCV data
        """
        # Normalize interval to standard format
        timeframe = normalize_interval(interval)

        # Only intraday intervals are supported by this method
        intraday_intervals = [
            TimeFrame.MINUTE_1,
            TimeFrame.MINUTE_5,
            TimeFrame.MINUTE_15,
            TimeFrame.MINUTE_30,
            TimeFrame.HOUR_1,
            TimeFrame.HOUR_4,
        ]

        if timeframe not in intraday_intervals:
            if self.show_log:
                logger.error(
                    f"Invalid interval: {interval}. "
                    f"intraday() supports: m/1m, 5m, 15m, 30m, h/1h, 4h. "
                    f"Use history() for EOD data (d/1d, w/1w, M/1M)."
                )
            return None

        # Map TimeFrame to FMP API endpoint
        timeframe_to_fmp_endpoint = {
            TimeFrame.MINUTE_1: 'historical-chart/1min',
            TimeFrame.MINUTE_5: 'historical-chart/5min',
            TimeFrame.MINUTE_15: 'historical-chart/15min',
            TimeFrame.MINUTE_30: 'historical-chart/30min',
            TimeFrame.HOUR_1: 'historical-chart/1hour',
            TimeFrame.HOUR_4: 'historical-chart/4hour',
        }

        # Build complete API URL
        # Example: https://financialmodelingprep.com/stable/
        # historical-chart/1min
        interval_path = timeframe_to_fmp_endpoint[timeframe]
        url = (f"{self.config.domain}/{interval_path}?"
               f"symbol={self.symbol}&apikey={self.config.api_key}")

        # Add date filters if provided
        if start:
            url = f"{url}&from={start}"
        if end:
            url = f"{url}&to={end}"

        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log or False)

        if df is not None and not df.empty:
            # Normalize column names to vnstock standard
            df = self._normalize_ohlcv_columns(df)

            # Ensure date column is datetime
            if 'time' in df.columns:
                df['time'] = pd.to_datetime(df['time'])
                df = df.sort_values('time', ascending=True).reset_index(
                    drop=True)

        return df

    def _normalize_ohlcv_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize OHLCV column names to vnstock standard format.

        Converts FMP column names to the standard vnstock naming convention
        for consistency across all data providers. Also converts camelCase
        column names to snake_case.

        Args:
            df (pd.DataFrame): DataFrame with FMP column names

        Returns:
            pd.DataFrame: DataFrame with standardized vnstock column names
                         in snake_case format
        """
        # Rename columns according to vnstock mapping
        rename_dict = {}
        for fmp_col, vnstock_col in _OHLCV_MAP.items():
            if fmp_col in df.columns:
                rename_dict[fmp_col] = vnstock_col

        if rename_dict:
            df = df.rename(columns=rename_dict)

        # Convert all remaining camelCase column names to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]

        return df


# Register FMP Quote provider
from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401
ProviderRegistry.register('quote', 'fmp', Quote)
