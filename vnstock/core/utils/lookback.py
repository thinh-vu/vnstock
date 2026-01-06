
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple, Union
from vnstock.core.utils.logger import get_logger

logger = get_logger(__name__)

# ===========================================
# 📅 TIME MILESTONES DEFINITION
# ===========================================

# Common financial analysis timeframes converted to days
TIME_MILESTONES = {
    '1W': 7,      # 1 week
    '2W': 14,     # 2 weeks
    '3W': 21,     # 3 weeks
    '1M': 30,     # 1 month
    '6W': 45,     # 6 weeks
    '2M': 60,     # 2 months
    '3M': 90,     # 1 quarter
    '4M': 120,    # 4 months
    '5M': 150,    # 5 months
    '6M': 180,    # 6 months (half year)
    '9M': 270,    # 9 months (3 quarters)
    '1Y': 365,    # 1 year
    '18M': 540,   # 1.5 years
    '2Y': 730,    # 2 years
    '3Y': 1095,   # 3 years
    '5Y': 1825,   # 5 years
}

# Estimated ratio of (Calendar Days / Data Points) for different resolutions
# Based on Vietnam market trading hours and holidays (e.g., Tet holiday)
# 1D: ~250 trading days/year -> 365/250 = 1.46 ~ 1.5
# 1H: ~4-5 hours trading/day.
RESOLULTION_DAY_RATIOS = {
    '1D': 1.5,
    '1H': 0.3,
    '1W': 7.3,  # 52 weeks ~ 365 days -> ~7 calendar days per weekly bar
    '1M': 30.5, # 1 bar = 1 month -> ~30.5 calendar days per monthly bar
    'D': 1.5,
    'H': 0.3,
    'W': 7.3,
    'M': 30.5
}

def parse_flexible_lookback(length_str: str) -> int:
    """
    Parse a flexible lookback string like '10W', '2Y' into days.
    
    Args:
        length_str: String specifying length (e.g. '10W').
        
    Returns:
        int: Number of days. Returns 0 if parsing fails.
    """
    length_str = length_str.upper().strip()
    
    # Check milestones first for exact matches/standard definitions
    if length_str in TIME_MILESTONES:
        return TIME_MILESTONES[length_str]
        
    # Dynamic parsing using regex
    # Match number followed by unit (D, W, M, Q, Y)
    match = re.match(r"^(\d+)([DWMQY])$", length_str)
    
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit == 'D':
            return value
        elif unit == 'W':
            return value * 7
        elif unit == 'M':
             # Approximation: 30 days
            return value * 30
        elif unit == 'Q':
            return value * 90
        elif unit == 'Y':
            return value * 365
            
    return 0

def round_to_milestone(days: int) -> Tuple[int, str]:
    """
    Round the number of days to the nearest standard time milestone.
    
    Args:
        days (int): Number of days to round
    
    Returns:
        tuple: (rounded_days, milestone_name)
    """
    sorted_milestones = sorted(TIME_MILESTONES.items(), key=lambda x: x[1])
    
    if days <= 0:
        return 0, ""

    closest_milestone = min(sorted_milestones, key=lambda x: abs(x[1] - days))
    
    return closest_milestone[1], closest_milestone[0]

def get_start_date_from_lookback(
    lookback_days: Optional[int] = None,
    lookback_length: Optional[Union[str, int]] = None,
    bars: Optional[int] = None,
    interval: str = '1D',
    end_date: Optional[str] = None,
    use_milestone_rounding: bool = True
) -> str:
    """
    Calculate start date based on lookback criteria (days, length string/int, or bar count).
    
    Priority: lookback_days > lookback_length > bars.
    
    Args:
        lookback_days (int): Exact number of calendar days to look back.
        lookback_length (str|int): Length of lookback. 
                                  Can be a period string (e.g. '3M', '1Y') 
                                  or integer/numeric string representing days (e.g. 150, '150').
        bars (int): Number of data bars (candles) desired.
        interval (str): Data resolution ('1D', '1H', etc) used for bar conversion.
        end_date (str): End date string 'YYYY-MM-DD'. Defaults to today.
        use_milestone_rounding (bool): Whether to round calculated days (from bars) to nearest milestone.
        
    Returns:
        str: Start date in 'YYYY-MM-DD' format.
    """
    days = 0
    
    # 1. Use explicit days if provided
    if lookback_days is not None:
        days = lookback_days
        
    # 2. Use length if provided (handles both '3M' and 150/'150')
    elif lookback_length is not None:
        is_numeric = False
        if isinstance(lookback_length, int):
            is_numeric = True
            days = lookback_length
        elif isinstance(lookback_length, str) and lookback_length.isdigit():
            is_numeric = True
            days = int(lookback_length)
            
        if not is_numeric:
            parsed_days = parse_flexible_lookback(lookback_length)
            if parsed_days > 0:
                days = parsed_days
            else:
                raise ValueError(f"Invalid lookback_length '{lookback_length}'. "
                                 "Format must be 'Nb' (bars) or 'N[D/W/M/Q/Y]' (e.g., '10W', '3M').")

    # 3. Convert bars to days
    elif bars is not None:
        ratio = 1.5 # Default 1D
        
        # Simple interval normalization
        if 'D' in interval or 'd' in interval:
            ratio = RESOLULTION_DAY_RATIOS['1D']
        elif 'H' in interval or 'h' in interval:
            ratio = RESOLULTION_DAY_RATIOS['1H']
        elif 'W' in interval or 'w' in interval:
            ratio = RESOLULTION_DAY_RATIOS['1W']
        elif 'M' in interval: 
            if 'm' in interval and 'M' not in interval: # minute
                 ratio = 0.006 
            else:
                ratio = RESOLULTION_DAY_RATIOS['1M']
        
        raw_days = int(bars * ratio)
        
        if use_milestone_rounding:
            rounded_days, _ = round_to_milestone(raw_days)
            days = rounded_days
        else:
            days = raw_days

    if days <= 0:
         days = 1

    # Calculate actual date
    if end_date:
        try:
            if len(end_date) > 10:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            else:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            end_dt = datetime.now()
    else:
        end_dt = datetime.now()
        
    start_dt = end_dt - timedelta(days=days)
    return start_dt.strftime("%Y-%m-%d")

def interpret_lookback_length(length: Union[str, int]) -> Tuple[Optional[int], Optional[Union[str, int]]]:
    """
    Interpret the lookback length input to separate bars from days/periods.
    
    Args:
        length: Input length (e.g., '100b', 150, '3M')
        
    Returns:
        tuple: (bars, days_or_period)
            - bars: Integer number of bars if specified (e.g. '100b' -> 100), else None.
            - days_or_period: Original length if not bars, else None.
    """
    if isinstance(length, str):
        # Check for 'b' or 'bar' suffix (case insensitive)
        if length.lower().endswith('b'):
            try:
                return int(length[:-1]), None
            except ValueError:
                pass
        elif length.lower().endswith('bars'):
             try:
                return int(length[:-4]), None
             except ValueError:
                 pass
                 
    return None, length
