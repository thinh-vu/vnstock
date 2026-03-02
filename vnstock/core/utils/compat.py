"""
Pandas compatibility utilities for handling differences across versions.

Supports pandas 1.x through 2.2+ with graceful fallbacks for deprecated methods.
Compatible with Python 3.10+.
"""

import pandas as pd
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

# Get pandas version
PANDAS_VERSION = tuple(int(x) for x in pd.__version__.split('.')[:3])
PANDAS_GE_210 = PANDAS_VERSION >= (2, 1, 0)
PANDAS_GE_220 = PANDAS_VERSION >= (2, 2, 0)


def apply_to_dataframe(
    df: pd.DataFrame,
    func: Callable[[Any], Any],
    method: str = "auto"
) -> pd.DataFrame:
    """
    Apply a function to all elements in a DataFrame with pandas version compatibility.

    Automatically handles the transition from deprecated `applymap()` (pandas <2.1)
    to `map()` (pandas >=2.1).

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame to transform
    func : Callable
        Function to apply to each element. Should handle any type gracefully.
    method : str, optional
        Method to use: 'auto' (default) detects automatically, 'map' forces map(),
        'applymap' forces applymap()

    Returns
    -------
    pd.DataFrame
        Transformed DataFrame

    Examples
    --------
    >>> df = pd.DataFrame({'A': ['x\\ny', 'a\\nb']})
    >>> result = apply_to_dataframe(df, lambda x: x.replace('\\n', ' ') if isinstance(x, str) else x)
    >>> print(result)
           A
    0  x y
    1  a b
    """
    if method == "auto":
        # Try map() first (pandas 2.1+)
        if PANDAS_GE_210 and hasattr(df, 'map'):
            try:
                return df.map(func)
            except (AttributeError, TypeError) as e:
                logger.debug(f"map() failed, falling back to applymap(): {e}")
        
        # Fallback to applymap() (pandas <2.1)
        if hasattr(df, 'applymap'):
            return df.applymap(func)
        else:
            # If neither is available, raise an error
            raise AttributeError(
                f"DataFrame has neither 'map' nor 'applymap' methods. "
                f"Pandas version: {pd.__version__}"
            )
    
    elif method == "map":
        if hasattr(df, 'map'):
            return df.map(func)
        else:
            logger.warning(
                f"DataFrame.map() not available in pandas {pd.__version__}, "
                "falling back to applymap()"
            )
            return df.applymap(func)
    
    elif method == "applymap":
        if hasattr(df, 'applymap'):
            return df.applymap(func)
        else:
            logger.warning(
                f"DataFrame.applymap() deprecated in pandas {pd.__version__}, "
                "using map() instead"
            )
            return df.map(func)
    
    else:
        raise ValueError(f"Unknown method: {method}. Use 'auto', 'map', or 'applymap'")


def get_pandas_info() -> dict:
    """
    Get pandas version and compatibility information.

    Returns
    -------
    dict
        Dictionary with version info and feature availability
    """
    return {
        "version": pd.__version__,
        "version_tuple": PANDAS_VERSION,
        "has_map": hasattr(pd.DataFrame, 'map'),
        "has_applymap": hasattr(pd.DataFrame, 'applymap'),
        "ge_210": PANDAS_GE_210,
        "ge_220": PANDAS_GE_220,
    }


# Convenience functions for common string replacement operations
def replace_newlines_in_dataframe(df: pd.DataFrame, replacement: str = ' ') -> pd.DataFrame:
    """
    Replace newline characters with a string in all DataFrame columns.

    Handles string columns only, passes through non-string values unchanged.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    replacement : str, optional
        String to replace newlines with (default: ' ')

    Returns
    -------
    pd.DataFrame
        DataFrame with newlines replaced in all string columns

    Examples
    --------
    >>> df = pd.DataFrame({'col': ['a\\nb', 'c\\nd']})
    >>> result = replace_newlines_in_dataframe(df)
    >>> print(result)
      col
    0 a b
    1 c d
    """
    def _replace_fn(x):
        if isinstance(x, str):
            return x.replace('\n', replacement)
        return x
    
    return apply_to_dataframe(df, _replace_fn)


def strip_whitespace_in_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strip leading/trailing whitespace from all string columns in DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame

    Returns
    -------
    pd.DataFrame
        DataFrame with whitespace stripped from all string columns
    """
    def _strip_fn(x):
        if isinstance(x, str):
            return x.strip()
        return x
    
    return apply_to_dataframe(df, _strip_fn)


def normalize_frequency_string(freq_str: str) -> str:
    """
    Normalize pandas frequency strings for compatibility across versions.

    Handles the transition from deprecated frequency names (pandas <2.2)
    to new names (pandas >=2.2), including:
    - 'M' → 'ME' (month end)
    - 'H' → 'h' (handled by pandas)
    - 'D' → 'd' (handled by pandas)

    Parameters
    ----------
    freq_str : str
        Original frequency string (e.g., 'M', '1M', 'ME', '1ME')

    Returns
    -------
    str
        Normalized frequency string compatible with current pandas version

    Notes
    -----
    - This function is pandas version-aware and uses the best format for
      the installed pandas version
    - If pandas >=2.2, 'M' is automatically converted to 'ME'
    - The function is safe to call multiple times (idempotent)

    Examples
    --------
    >>> normalize_frequency_string('M')  # pandas < 2.2
    'M'
    >>> normalize_frequency_string('M')  # pandas >= 2.2
    'ME'
    >>> normalize_frequency_string('ME')  # Already normalized
    'ME'
    """
    if not isinstance(freq_str, str):
        return freq_str
    
    # For pandas 2.2+, 'M' is no longer supported, use 'ME' instead
    if PANDAS_GE_220:
        # Replace 'M' with 'ME' but only for month-end frequency
        # Be careful with patterns like '5min', '1H', etc.
        if freq_str.endswith('M') and not any(freq_str.endswith(x) for x in ['min', 'h']):
            # It's a month frequency like 'M', '1M', etc.
            if freq_str == 'M':
                return 'ME'
            elif freq_str.endswith('M'):
                # Handle cases like '1M', '2M', etc.
                prefix = freq_str[:-1]  # Get everything except the last 'M'
                return f'{prefix}ME'
    
    return freq_str


def safe_resample_dataframe(
    df: pd.DataFrame,
    freq: str,
    time_col: str = 'time',
    agg_rules: dict = None
) -> pd.DataFrame:
    """
    Safely resample a DataFrame with pandas version compatibility.

    Handles frequency string normalization and resampling across different
    pandas versions.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with time series data
    freq : str
        Frequency string (e.g., 'M', 'ME', 'D', 'H', '5min')
    time_col : str, optional
        Name of the time column (default: 'time')
    agg_rules : dict, optional
        Aggregation rules for resampling. If None, uses OHLCV defaults

    Returns
    -------
    pd.DataFrame
        Resampled DataFrame

    Raises
    ------
    KeyError
        If time_col is not in DataFrame
    ValueError
        If frequency string is invalid

    Examples
    --------
    >>> df = pd.DataFrame({'time': pd.date_range('2024-01-01', periods=100),
    ...                     'close': range(100)})
    >>> resampled = safe_resample_dataframe(df, 'D')
    """
    if time_col not in df.columns:
        raise KeyError(f"Time column '{time_col}' not found in DataFrame")
    
    # Normalize frequency string for current pandas version
    normalized_freq = normalize_frequency_string(freq)
    
    # Default OHLCV aggregation rules
    if agg_rules is None:
        agg_rules = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
        }
    
    # Build aggregation dict for available columns
    agg_dict = {}
    for col in df.columns:
        if col == time_col:
            continue
        agg_dict[col] = agg_rules.get(col, 'last')
    
    # Perform resampling
    try:
        df_resampled = df.set_index(time_col).resample(normalized_freq).agg(agg_dict)
        df_resampled = df_resampled.reset_index()
        return df_resampled
    except ValueError as e:
        # If frequency still fails, provide helpful error message
        logger.error(
            f"Resampling failed with frequency '{normalized_freq}' "
            f"(original: '{freq}') on pandas {pd.__version__}: {e}"
        )
        raise
