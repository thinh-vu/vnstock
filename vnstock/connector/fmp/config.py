"""
Configuration and utility functions for FMP API connector.

Provides classes and functions for FMP API interaction including
configuration management and HTTP request handling.
Following VCI patterns for consistency.
"""

import os
import requests
import pandas as pd
from pandas import json_normalize
from typing import Optional
from vnstock.core.utils.logger import get_logger
from .const import _FMP_DOMAIN, _ENDPOINTS, _DEFAULT_TIMEOUT

logger = get_logger(__name__)

FMP_DOMAIN = 'https://financialmodelingprep.com/stable'


class FMPConfig:
    """
    Configuration management for FMP API connector.

    Handles API configuration including API key retrieval from environment
    variables and provides utilities for building API URLs.
    Following VCI patterns for consistency.
    """

    def __init__(self, api_key: Optional[str] = None,
                 show_log: Optional[bool] = True):
        """
        Initialize FMP configuration.

        Args:
            api_key (Optional[str]): FMP API key from environment or parameter
            show_log (Optional[bool]): Whether to display logging messages
        """
        self.api_key = api_key or self._get_api_key()
        self.domain = _FMP_DOMAIN
        self.timeout = _DEFAULT_TIMEOUT
        self.show_log = show_log

        if not show_log:
            logger.setLevel('CRITICAL')

    def _get_api_key(self) -> str:
        """
        Retrieve FMP API key from environment variables.

        Attempts to load API key from FMP_TOKEN or FMP_API_KEY environment
        variables. Raises an error if no API key is found.

        Returns:
            str: API key for FMP API authentication

        Raises:
            ValueError: If no API key found in environment variables
        """
        # Try FMP_TOKEN first (like in terminal)
        api_key = os.getenv('FMP_TOKEN')
        if not api_key:
            api_key = os.getenv('FMP_API_KEY')

        if api_key:
            if self.show_log:
                logger.info("Using API key from environment variable")
            return api_key

        # No API key found - raise error with instructions
        error_msg = (
            "FMP API key not found in environment variables.\n"
            "Please set one of the following environment variables:\n"
            "  - export FMP_API_KEY='your_api_key_here'\n"
            "  - export FMP_TOKEN='your_api_key_here'\n"
            "\n"
            "Or pass api_key directly to FMPQuote:\n"
            "  quote = FMPQuote(symbol='AAPL', api_key='your_key')\n"
            "\n"
            "Get your API key at: https://financialmodelingprep.com"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    def get_endpoint_url(self, endpoint_name: str,
                         symbol: Optional[str] = None,
                         query: Optional[str] = None) -> str:
        """
        Build complete API endpoint URL.

        Constructs full FMP API URL with parameters according to new format.
        Format: https://financialmodelingprep.com/stable/endpoint?params

        Args:
            endpoint_name (str): Endpoint name key from _ENDPOINTS mapping
            symbol (Optional[str]): Stock ticker symbol (if applicable)
            query (Optional[str]): Search query string for search endpoints

        Returns:
            str: Complete API URL with parameters

        Raises:
            ValueError: If endpoint_name not found in _ENDPOINTS mapping
        """
        if endpoint_name not in _ENDPOINTS:
            raise ValueError(f"Endpoint not found: {endpoint_name}")

        endpoint = _ENDPOINTS[endpoint_name]
        url = f"{self.domain}{endpoint}"

        # Build query parameters
        params = []

        if query:
            # For search endpoint
            params.append(f"query={query}")
        elif symbol:
            # For endpoints requiring symbol
            params.append(f"symbol={symbol}")

        # Add API key authentication
        params.append(f"apikey={self.api_key}")

        # Join parameters into URL
        url = f"{url}?{'&'.join(params)}"
        return url


def make_fmp_request(url: str, timeout: int = _DEFAULT_TIMEOUT,
                     show_log: bool = True) -> Optional[pd.DataFrame]:
    """
    Execute HTTP request to FMP API and return data as DataFrame.

    Handles API communication including error handling for various HTTP
    status codes and response data formats. Following VCI patterns for
    consistent error handling and logging.

    Args:
        url (str): Complete API URL with all parameters
        timeout (int): Request timeout in seconds. Defaults to 30.
        show_log (bool): Whether to display logging messages

    Returns:
        Optional[pd.DataFrame]: Response data as DataFrame, or None on error
    """
    if show_log:
        logger.info(f"Gửi request tới: {url}")

    try:
        response = requests.get(url, timeout=timeout)

        if response.status_code == 200:
            data = response.json()

            if isinstance(data, list):
                if len(data) == 0:
                    if show_log:
                        logger.warning("API returned empty data")
                    return pd.DataFrame()
                return pd.DataFrame(data)

            elif isinstance(data, dict):
                # Handle historical data format from FMP API
                if 'historical' in data:
                    historical_data = data['historical']
                    df = pd.DataFrame(historical_data)
                    # Add metadata if available
                    if 'symbol' in data:
                        df['symbol'] = data['symbol']
                    return df
                else:
                    return json_normalize(data)
            else:
                if show_log:
                    logger.error(f"Unexpected data type: {type(data)}")
                return None

        elif response.status_code == 403:
            error_msg = (
                "API access denied. Check subscription plan."
            )
            if show_log:
                logger.error(error_msg)
            return None

        elif response.status_code == 429:
            error_msg = "Rate limit exceeded. Try again later."
            if show_log:
                logger.error(error_msg)
            return None

        else:
            error_msg = f"API Error {response.status_code}: {response.text}"
            if show_log:
                logger.error(error_msg)
            return None

    except requests.exceptions.Timeout:
        if show_log:
            logger.error("Request timeout")
        return None

    except requests.exceptions.RequestException as e:
        if show_log:
            logger.error(f"Request failed: {e}")
        return None

    except Exception as e:
        if show_log:
            logger.error(f"Unexpected error: {e}")
        return None


def normalize_dataframe(df: pd.DataFrame,
                        date_columns: Optional[list] = None,
                        show_log: bool = True) -> pd.DataFrame:
    """
    Normalize DataFrame: convert date and numeric columns.

    Standardizes data types for date, numeric, and symbol columns to ensure
    consistency across all FMP API responses.

    Args:
        df (pd.DataFrame): DataFrame to normalize
        date_columns (Optional[list]): List of date columns to convert.
                                       If None, uses default date columns.
        show_log (bool): Whether to display logging messages

    Returns:
        pd.DataFrame: Normalized DataFrame with standardized types
    """
    if df is None or df.empty:
        return df

    from .const import _DATE_COLUMNS

    # Convert date columns to datetime type
    if date_columns is None:
        date_columns = _DATE_COLUMNS

    for col in date_columns:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except Exception as e:
                if show_log:
                    logger.warning(
                        f"Cannot convert {col} to datetime: {e}"
                    )

    # Convert symbol column to uppercase
    if 'symbol' in df.columns:
        df['symbol'] = df['symbol'].str.upper()

    # Convert numeric columns from string if needed
    numeric_candidates = [
        'price', 'change', 'changePercentage', 'volume',
        'marketCap', 'revenue', 'netIncome', 'eps'
    ]

    for col in numeric_candidates:
        if col in df.columns and df[col].dtype == 'object':
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except Exception:
                pass

    return df
