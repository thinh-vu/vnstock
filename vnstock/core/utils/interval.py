"""
Interval/TimeFrame utility functions.

Provides unified interval conversion across vnstock library.
Supports multiple input formats with standardized aliases:

Aliases (case-sensitive):
- m or 1m/5m/15m/30m → MINUTE
- h or 1H → HOUR
- d or 1D → DAY
- w or 1W → WEEK
- M or 1M → MONTH (capital M only)

Formats:
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

    Standard aliases (case-sensitive):
    - m or 1m/5m/15m/30m → TimeFrame.MINUTE_*
    - h or 1H → TimeFrame.HOUR_*
    - d or 1D → TimeFrame.DAY_1
    - w or 1W → TimeFrame.WEEK_1
    - M or 1M → TimeFrame.MONTH_1

    Also supports human readable: 'day', 'hour', 'minute', 'week', 'month'
    None defaults to TimeFrame.DAY_1

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
        >>> normalize_interval('d')
        <TimeFrame.DAY_1: '1D'>
        >>> normalize_interval('M')
        <TimeFrame.MONTH_1: '1M'>
    """
    if interval is None:
        return TimeFrame.DAY_1

    # Already TimeFrame enum
    if isinstance(interval, TimeFrame):
        return interval

    interval_orig = str(interval)
    interval_str = interval_orig.lower().strip()

    # Standard aliases (case-sensitive for M vs m):
    # m/1m/5m/15m/30m = MINUTE, M/1M = MONTH
    # h/1H = HOUR, d/1D = DAY, w/1W = WEEK
    
    # Handle MONTH: capital M only
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
    }

    result = interval_map.get(interval_str)
    if result is not None:
        return result

    # If not found, raise error
    msg = (f"Invalid interval: {interval}. "
           f"Use TimeFrame enum or formats like: "
           f"1D, 1H, 1W, 1M (vnstock), "
           f"d, h, m, w, M (alias - case-sensitive), "
           f"or day, hour, minute, week, month (human readable)")
    raise ValueError(msg)


def get_interval_aliases() -> dict:
    """
    Get all supported interval aliases (case-sensitive).

    Returns:
        dict: Mapping of alias → TimeFrame enum
        - m → MINUTE_1
        - h → HOUR_1
        - d → DAY_1
        - w → WEEK_1
        - M → MONTH_1 (capital M)

    Examples:
        >>> aliases = get_interval_aliases()
        >>> aliases['d']
        <TimeFrame.DAY_1: '1D'>
        >>> aliases['M']
        <TimeFrame.MONTH_1: '1M'>
    """
    return {
        'm': TimeFrame.MINUTE_1,
        'h': TimeFrame.HOUR_1,
        'd': TimeFrame.DAY_1,
        'w': TimeFrame.WEEK_1,
        'M': TimeFrame.MONTH_1,
    }
