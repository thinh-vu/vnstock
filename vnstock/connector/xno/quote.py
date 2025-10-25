"""
XNO Quote connector for vnstock.

Quote module for XNO data source.

Provides access to historical and real-time price data from XNO API.
Implements standard vnstock interface with unified parameter naming.
"""

import pandas as pd
from typing import Optional, Union
from vnai import optimize_execution
from vnstock.core.base.registry import ProviderRegistry
from vnstock.core.types import DataCategory, ProviderType, TimeFrame
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.validation import validate_symbol
from .config import XNOConfig, make_xno_request, normalize_xno_dataframe
from .const import _OHLC_RENAME

logger = get_logger(__name__)


@ProviderRegistry.register(DataCategory.QUOTE, "xno", ProviderType.API)
class Quote:
    """
    Historical and real-time price data provider for XNO.

    Implements standard vnstock Quote interface with unified parameter names
    (start, end, interval) compatible with all vnstock providers.

    Supports TimeFrame enum from vnstock.core.types and XNO-style aliases
    (m, h, d, w, M) for backward compatibility.

    Uses only 2 dedicated XNO endpoints:
    - API v2: /quant-data/v1/stocks/{symbol}/ohlcv/{interval}
    - Lambda: /LEData/getAll, /AccumulatedPriceStepVol/getSymbolData

    Parameters:
        symbol (str): Stock symbol (e.g., 'VNM', 'FPT')
        api_key (Optional[str]): XNO API key (reads from env if not provided)
        show_log (Optional[bool]): Display log messages. Default is False.

    Examples:
        >>> quote = Quote('VNM')
        >>> df = quote.history(start='2024-01-01', end='2024-12-31')
        >>> df = quote.history(interval=TimeFrame.HOUR_1)
        >>> df = quote.intraday()
        >>> df = quote.price_depth()
    """

    def __init__(
        self,
        symbol: str,
        api_key: Optional[str] = None,
        show_log: Optional[bool] = False
    ):
        """Initialize Quote instance."""
        self.symbol = validate_symbol(symbol)
        self.data_source = 'XNO'
        self.config = XNOConfig(api_key=api_key, show_log=show_log)
        self.show_log = show_log

        if not show_log:
            logger.setLevel('CRITICAL')

    def _normalize_interval(
        self,
        interval: Union[str, TimeFrame, None]
    ) -> str:
        """
        Normalize interval to XNO format.

        Converts any supported format (TimeFrame enum, vnstock format,
        alias shortcuts) to XNO API format (m, h, d, w, M).

        Supports:
        - TimeFrame enum: TimeFrame.DAY_1 → 'd'
        - vnstock: '1D', '1H', '1W', '1M', '1m', '5m' → 'd', 'h', 'w', 'M'
        - Alias: 'm', 'h', 'd', 'w', 'M' → unchanged
        - Human readable: 'day', 'hour', 'minute' → 'd', 'h', 'm'
        - None → 'd' (default)

        Args:
            interval: Interval in any supported format

        Returns:
            XNO format: m, h, d, w, M

        Raises:
            ValueError: If interval format is not recognized
        """
        if interval is None:
            return 'd'

        # Use centralized interval normalization
        from vnstock.core.utils.interval import normalize_interval as norm
        timeframe = norm(interval)

        # Map TimeFrame to XNO format
        timeframe_to_xno = {
            TimeFrame.MINUTE_1: 'm',
            TimeFrame.MINUTE_5: 'm',
            TimeFrame.MINUTE_15: 'm',
            TimeFrame.MINUTE_30: 'm',
            TimeFrame.HOUR_1: 'h',
            TimeFrame.HOUR_4: 'h',
            TimeFrame.DAY_1: 'd',
            TimeFrame.DAILY: 'd',
            TimeFrame.WEEK_1: 'w',
            TimeFrame.WEEKLY: 'w',
            TimeFrame.MONTH_1: 'M',
            TimeFrame.MONTHLY: 'M',
        }

        result = timeframe_to_xno.get(timeframe)
        if result:
            return result

        # Fallback error
        msg = (f"Unsupported TimeFrame: {timeframe}. "
               f"Contact support if this should be supported.")
        logger.error(msg)
        raise ValueError(msg)

    @optimize_execution("XNO")
    def history(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        interval: Union[str, TimeFrame] = 'd',
        show_log: Optional[bool] = None,
        count_back: Optional[int] = None,
        floating: int = 2
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data.

        Uses unified vnstock parameter names (start, end, interval).
        Supports both TimeFrame enum and XNO-style aliases.

        Parameters:
            start (Optional[str]): Start date in YYYY-MM-DD format.
                                  If None, fetches from earliest.
            end (Optional[str]): End date in YYYY-MM-DD format.
                                If None, fetches to latest.
            interval (Union[str, TimeFrame]): Time interval.
                                             Accepts:
                                             - TimeFrame enum
                                             - vnstock: '1D', '1H', '1W', '1M'
                                             - Alias: 'd', 'h', 'm', 'w', 'M'
                                             Default: 'd' (daily)
            show_log (Optional[bool]): Display logs. If None, uses instance.
            count_back (Optional[int]): Limit bars returned. If None, all.
            floating (int): Decimal precision. Default is 2.

        Returns:
            Optional[pd.DataFrame]: DataFrame with columns:
                                   [time, open, high, low, close, volume]
                                   Returns None if request fails.

        Examples:
            >>> df = quote.history()  # All daily data
            >>> df = quote.history(start='2024-01-01', end='2024-12-31')
            >>> df = quote.history(interval=TimeFrame.HOUR_1)
            >>> df = quote.history(interval='1H')  # vnstock format
            >>> df = quote.history(interval='h')   # XNO alias
            >>> df = quote.history(count_back=100)  # Last 100 bars
        """
        show_log = show_log if show_log is not None else self.show_log

        # Normalize interval
        xno_interval = self._normalize_interval(interval)

        # Build URL - XNO API v2 endpoint
        url = (f"{self.config.api_base}/quant-data/v1/stocks/"
               f"{self.symbol}/ohlcv/{xno_interval}")
        headers = self.config.get_headers()

        # Build params
        params = {}
        if start:
            params['from'] = int(pd.Timestamp(start).timestamp())
        else:
            params['from'] = 0

        if end:
            params['to'] = int(pd.Timestamp(end).timestamp())
        else:
            params['to'] = 9999999999

        if count_back:
            params['countBack'] = count_back

        # Build query string
        query_str = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{query_str}"

        if show_log:
            msg = f"Fetching {self.symbol} history from {start} to {end}"
            logger.info(msg)

        # Make request
        df = make_xno_request(
            full_url,
            headers=headers,
            timeout=self.config.timeout,
            show_log=bool(show_log)
        )

        if df is not None and not df.empty:
            # Normalize columns
            df = self._normalize_ohlcv_columns(df)

            # Normalize dates
            df = normalize_xno_dataframe(df, show_log=bool(show_log))

            # Apply floating point precision
            for col in ['open', 'high', 'low', 'close']:
                if col in df.columns:
                    df[col] = df[col].round(floating)

            # Sort by time
            if 'time' in df.columns:
                df = df.sort_values('time').reset_index(drop=True)

            if show_log:
                logger.info(f"Fetched {len(df)} records")

        return df

    @optimize_execution("XNO")
    def intraday(
        self,
        page_size: Optional[int] = 100,
        last_time: Optional[str] = None,
        show_log: Optional[bool] = None
    ) -> Optional[pd.DataFrame]:
        """
        Fetch intraday/real-time trading data.

        Returns current trading session data with optional pagination.
        Only available during trading hours.

        Parameters:
            page_size (Optional[int]): Records per request. Default is 100.
            last_time (Optional[str]): Resume from this time for pagination.
                                      Format: 'YYYY-MM-DD HH:MM:SS'
            show_log (Optional[bool]): Display logs. If None, uses instance.

        Returns:
            Optional[pd.DataFrame]: Intraday trading data.
                                   Returns None if fails or market closed.

        Examples:
            >>> df = quote.intraday()
            >>> df = quote.intraday(page_size=50)
            >>> df = quote.intraday(last_time='2024-10-23 14:30:00')
        """
        show_log = show_log if show_log is not None else self.show_log

        # Build URL - XNO Lambda endpoint
        url = f"{self.config.lambda_base}/LEData/getAll"
        headers = self.config.get_headers()

        # Build params
        params = {
            'symbol': self.symbol,
            'pageSize': page_size or 100
        }

        if last_time:
            params['lastTime'] = last_time

        # Build query string
        query_str = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{query_str}"

        if show_log:
            logger.info(f"Fetching intraday data for {self.symbol}")

        # Make request
        df = make_xno_request(
            full_url,
            headers=headers,
            timeout=self.config.timeout,
            show_log=bool(show_log)
        )

        if df is not None and not df.empty:
            # Rename columns if needed
            df = self._normalize_ohlcv_columns(df)

            # Normalize dates
            df = normalize_xno_dataframe(df, show_log=bool(show_log))

            if show_log:
                logger.info(f"Fetched {len(df)} intraday records")

        return df

    @optimize_execution("XNO")
    def price_depth(
        self,
        show_log: Optional[bool] = None
    ) -> Optional[pd.DataFrame]:
        """
        Fetch order book depth (bid-ask levels).

        Returns real-time order book with bid/ask levels and volumes.
        Only available during trading hours.

        Parameters:
            show_log (Optional[bool]): Display logs. If None, uses instance.

        Returns:
            Optional[pd.DataFrame]: Order book depth data with bid/ask levels.
                                   Returns None if fails or market closed.

        Examples:
            >>> df = quote.price_depth()
            >>> df = quote.price_depth(show_log=True)
        """
        show_log = show_log if show_log is not None else self.show_log

        # Build URL - XNO Lambda endpoint
        url_path = 'AccumulatedPriceStepVol/getSymbolData'
        url = f"{self.config.lambda_base}/{url_path}"
        headers = self.config.get_headers()

        # Build params
        params = {'symbol': self.symbol}

        # Build query string
        query_str = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{query_str}"

        if show_log:
            logger.info(f"Fetching price depth for {self.symbol}")

        # Make request
        df = make_xno_request(
            full_url,
            headers=headers,
            timeout=self.config.timeout,
            show_log=bool(show_log)
        )

        if df is not None and not df.empty:
            if show_log:
                logger.info(f"Fetched price depth with {len(df)} levels")

        return df

    def _normalize_ohlcv_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize OHLCV column names to vnstock standard.

        Parameters:
            df (pd.DataFrame): DataFrame to normalize

        Returns:
            pd.DataFrame: DataFrame with standardized column names
        """
        # Rename columns from mapping
        rename_dict = {}
        for xno_col, vnstock_col in _OHLC_RENAME.items():
            if xno_col in df.columns:
                rename_dict[xno_col] = vnstock_col

        if rename_dict:
            df = df.rename(columns=rename_dict)

        # Convert epoch timestamp to datetime for 'time' column
        if 'time' in df.columns:
            # Check if it's numeric (epoch)
            if pd.api.types.is_numeric_dtype(df['time']):
                # Determine if seconds or milliseconds
                sample = (df['time'].dropna().iloc[0]
                          if len(df) > 0 else 0)
                unit = 'ms' if sample > 10_000_000_000 else 's'
                df['time'] = pd.to_datetime(df['time'], unit=unit,
                                            errors='coerce')

        # Ensure numeric columns
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Ensure column order
        standard_cols = ['time', 'open', 'high', 'low', 'close', 'volume']
        existing_cols = [c for c in standard_cols if c in df.columns]
        other_cols = [c for c in df.columns if c not in standard_cols]

        df = df[existing_cols + other_cols]

        return df
