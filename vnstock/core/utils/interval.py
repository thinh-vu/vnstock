"""
Interval/TimeFrame utility functions.

Provides unified interval conversion across vnstock library.
Supports multiple input formats:
- TimeFrame enum: TimeFrame.DAY_1
- vnstock format: '1D', '1H', '1W', '1M', '1m', '5m', etc.
- Alias format: 'd', 'h', 'm', 'w', 'M' (convenient shortcuts)
- Human readable: 'day', 'hour', 'minute', 'week', 'month'
"""

from typing import Union
from vnstock.core.types import TimeFrame


def normalize_interval(
    interval: Union[str, TimeFrame, None]
) -> TimeFrame:
    """
    Normalize any interval format to TimeFrame enum.

    Supports:
    - TimeFrame enum: TimeFrame.DAY_1 → TimeFrame.DAY_1
    - vnstock format: '1D', '1H', '1W', '1M', '1m', '5m' → TimeFrame enum
    - Alias: 'd', 'h', 'm', 'w', 'M' → TimeFrame enum
    - Human readable: 'day', 'hour', 'minute' → TimeFrame enum
    - None → TimeFrame.DAY_1 (default)

    Args:
        interval: Interval in any supported format

    Returns:
        TimeFrame enum value

    Raises:
        ValueError: If interval format is not recognized

    Examples:
        >>> normalize_interval(TimeFrame.HOUR_1)
        <TimeFrame.HOUR_1: '1H'>
        >>> normalize_interval('1H')
        <TimeFrame.HOUR_1: '1H'>
        >>> normalize_interval('h')
        <TimeFrame.HOUR_1: '1H'>
        >>> normalize_interval('hour')
        <TimeFrame.HOUR_1: '1H'>
    """
    if interval is None:
        return TimeFrame.DAY_1

    # Already TimeFrame enum
    if isinstance(interval, TimeFrame):
        return interval

    interval_orig = str(interval)
    interval_str = interval_orig.lower().strip()

    # Handle capital M for month before general lowercase processing
    # vnstock uses '1M' (capital) for month, not '1m'
    if interval_orig in ('M', '1M'):
        return TimeFrame.MONTH_1

    # Mapping: any input format → TimeFrame enum
    interval_map = {
        # Aliases (convenience)
        'm': TimeFrame.MINUTE_1,
        'h': TimeFrame.HOUR_1,
        'd': TimeFrame.DAY_1,
        'w': TimeFrame.WEEK_1,
        # Human readable
        'minute': TimeFrame.MINUTE_1,
        'hour': TimeFrame.HOUR_1,
        'day': TimeFrame.DAY_1,
        'week': TimeFrame.WEEK_1,
        'month': TimeFrame.MONTH_1,
        # vnstock format (lowercase for comparison)
        '1m': TimeFrame.MINUTE_1,
        '5m': TimeFrame.MINUTE_5,
        '15m': TimeFrame.MINUTE_15,
        '30m': TimeFrame.MINUTE_30,
        '1h': TimeFrame.HOUR_1,
        '4h': TimeFrame.HOUR_4,
        '1d': TimeFrame.DAY_1,
        '1w': TimeFrame.WEEK_1,
        '1mo': TimeFrame.MONTH_1,
        '1month': TimeFrame.MONTH_1,
        'mo': TimeFrame.MONTH_1,
    }

    result = interval_map.get(interval_str)
    if result is not None:
        return result

    # If not found, raise error
    msg = (f"Invalid interval: {interval}. "
           f"Use TimeFrame enum or formats like: "
           f"1D, 1H, 1W, 1M (vnstock), "
           f"d, h, m, w, M (alias), "
           f"or day, hour, minute, week, month (human readable)")
    raise ValueError(msg)


def get_interval_aliases() -> dict:
    """
    Get all supported interval aliases.

    Returns:
        dict: Mapping of alias → TimeFrame enum

    Examples:
        >>> aliases = get_interval_aliases()
        >>> aliases['d']
        <TimeFrame.DAY_1: 'D'>
    """
    return {
        'm': TimeFrame.MINUTE_1,
        'h': TimeFrame.HOUR_1,
        'd': TimeFrame.DAY_1,
        'w': TimeFrame.WEEK_1,
        'M': TimeFrame.MONTH_1,
    }
