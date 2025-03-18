"""Data transformation utilities for vnstock data sources."""

import pandas as pd
import pytz
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, time

# Vietnam timezone
vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')

def get_trading_date() -> datetime.date:
    """
    Determine the appropriate trading date based on current day and time in Vietnam timezone.
    
    Returns:
        - datetime.date: The appropriate trading date to use
    """
    # Get current time in Vietnam timezone
    now = datetime.now(vietnam_tz)
    weekday = now.weekday()  # Monday is 0, Sunday is 6
    current_time = now.time()
    
    if weekday >= 5:  # Weekend (Saturday or Sunday)
        # Calculate days to previous Friday
        days_to_subtract = weekday - 4
        return (now - timedelta(days=days_to_subtract)).date()
    elif weekday == 0 and current_time < time(8, 30):
        # Monday before 8:30 AM
        return (now - timedelta(days=3)).date()  # Previous Friday
    else:
        # Regular trading day
        return now.date()

def convert_to_vietnam_time(timestamp_series, unit='s'):
    """
    Convert timestamp values to Vietnam timezone.
    
    Parameters:
        - timestamp_series: Series of timestamp values
        - unit: Unit for timestamp conversion ('s' for seconds, 'ms' for milliseconds)
        
    Returns:
        - Series of datetime objects in Vietnam timezone
    """
    dt_series = pd.to_datetime(timestamp_series, unit=unit)
    return dt_series.dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')

def process_match_types(df, asset_type, source):
    """
    Process match_type labels with special handling for stock ATO/ATC transactions.
    """
    # Basic replacement - applies to all asset types
    if source == 'VCI':
        df['match_type'] = df['match_type'].replace({'b': 'Buy', 's': 'Sell'})
    elif source == 'TCBS':
        df['match_type'] = df['match_type'].replace({'BU': 'Buy', 'SD': 'Sell'})
    
    # Only process ATO/ATC for stock assets
    if asset_type == 'stock' and (
        ('unknown' in df['match_type'].values and source == 'VCI') or 
        ('' in df['match_type'].values and source == 'TCBS')
    ):
        # Sort by time to ensure correct order
        df = df.sort_values('time')
        
        # Create a date column for grouping by trading day
        df['date'] = df['time'].dt.date

        # Process each trading day separately
        for date in df['date'].unique():
            day_mask = df['date'] == date
            
            # Create unknown mask based on source
            if source == 'VCI':
                unknown_mask = (df['match_type'] == 'unknown') & day_mask
            else:  # TCBS
                unknown_mask = (df['match_type'] == '') & day_mask
            
            unknown_indices = df[unknown_mask].index
            
            if len(unknown_indices) > 0:
                # Morning session: Find transactions around 9:15 AM (9:10-9:20)
                morning_mask = unknown_mask & (df['time'].dt.hour == 9) & (df['time'].dt.minute >= 10) & (df['time'].dt.minute <= 20)
                morning_indices = df[morning_mask].index
                
                # Afternoon session: Find transactions around 2:45 PM (14:40-14:50)
                afternoon_mask = unknown_mask & (df['time'].dt.hour == 14) & (df['time'].dt.minute >= 40) & (df['time'].dt.minute <= 50)
                afternoon_indices = df[afternoon_mask].index
                
                # Label ATO for first morning session transaction
                if len(morning_indices) > 0:
                    ato_idx = df.loc[morning_indices, 'time'].idxmin()
                    df.loc[ato_idx, 'match_type'] = 'ATO'
                
                # Label ATC for last afternoon session transaction
                if len(afternoon_indices) > 0:
                    atc_idx = df.loc[afternoon_indices, 'time'].idxmax()
                    df.loc[atc_idx, 'match_type'] = 'ATC'
        
        # Remove the temporary date column
        df = df.drop(columns=['date'])
    
    return df

def ohlc_to_df(data: Dict[str, Any], column_map: Dict[str, str], dtype_map: Dict[str, str],
              asset_type: str, symbol: str, source: str, interval: str = "1D",
              floating: int = 2, resample_map: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """Convert OHLC data from any source to standardized DataFrame format."""
    if not data:
        raise ValueError("Input data is empty or not provided.")
        
    # Handle different data source formats
    if source == 'TCBS':
        # TCBS data is already a list of dictionaries
        df = pd.DataFrame(data)
        # Apply column mapping directly through rename
        df.rename(columns=column_map, inplace=True)
    else:
        # VCI and other sources
        # Select and rename columns using dictionary comprehension
        columns_of_interest = {key: column_map[key] for key in column_map.keys() if key in data}
        df = pd.DataFrame(data)[columns_of_interest.keys()].rename(columns=column_map)
    
    # Ensure all required columns exist
    required_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}. Available columns: {df.columns.tolist()}")
    
    # Standard column order
    df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
    
    # Time conversion - handle different formats based on source
    if 'time' in df.columns:
        if source == 'VCI':
            # VCI uses integer timestamps
            df['time'] = pd.to_datetime(df['time'].astype(int), unit='s').dt.tz_localize('UTC')
            df['time'] = df['time'].dt.tz_convert('Asia/Ho_Chi_Minh')
        else:
            # TCBS and others might use string formats
            df['time'] = pd.to_datetime(df['time'], errors='coerce')
    
    # Price scaling for non-index/derivative assets
    if asset_type not in ["index", "derivative"]:
        df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].div(1000)
    
    # Round price columns
    df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].round(floating)
    
    # Resample if needed
    if resample_map and interval not in ["1m", "1H", "1D"]:
        df = df.set_index('time').resample(resample_map[interval]).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).reset_index()
    
    # Apply data types
    for col, dtype in dtype_map.items():
        if col in df.columns:
            if dtype == "datetime64[ns]" and hasattr(df[col], 'dt') and df[col].dt.tz is not None:
                df[col] = df[col].dt.tz_localize(None)  # Remove timezone info
                if interval == "1D":
                    df[col] = df[col].dt.date
            df[col] = df[col].astype(dtype)
    
    # Add metadata
    df.name = symbol
    df.category = asset_type
    df.source = source
    
    return df

def intraday_to_df(data: List[Dict[str, Any]], column_map: Dict[str, str], 
                  dtype_map: Dict[str, str], symbol: str, asset_type: str, 
                  source: str) -> pd.DataFrame:
    """Convert intraday trading data to standardized DataFrame format."""
    # Early exit if no data
    if not data:
        empty_df = pd.DataFrame(columns=list(column_map.values()))
        empty_df.attrs['symbol'] = symbol
        empty_df.category = asset_type
        empty_df.source = source
        return empty_df
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Select and rename columns
    available_columns = [col for col in column_map.keys() if col in df.columns]
    if not available_columns:
        raise ValueError(f"None of the expected columns found in data. Expected: {list(column_map.keys())}, Found: {df.columns.tolist()}")
    
    df = df[available_columns]
    df.rename(columns={k: column_map[k] for k in available_columns}, inplace=True)
    
    # Handle time column based on source
    if 'time' in df.columns:
        trading_date = get_trading_date()
        
        if source == 'VCI':
            # VCI provides timestamps
            df['time'] = convert_to_vietnam_time(df['time'].astype(int))
        else:  # TCBS
            # Check if we have just time values (HH:MM:SS)
            sample_time = str(df['time'].iloc[0]) if not df.empty else ''
            
            if ':' in sample_time and len(sample_time) <= 8:
                # Time-only values, combine with trading_date
                df['time'] = df['time'].apply(
                    lambda x: datetime.combine(trading_date, datetime.strptime(x, '%H:%M:%S').time())
                    if isinstance(x, str) and ':' in x else pd.NaT
                )
                # Localize to Vietnam timezone
                df['time'] = df['time'].dt.tz_localize('Asia/Ho_Chi_Minh', ambiguous='NaT')
            else:
                # Parse as full datetime
                df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
                if df['time'].dt.tz is None:
                    df['time'] = df['time'].dt.tz_localize('Asia/Ho_Chi_Minh', ambiguous='NaT')
    
    # Process match types
    if 'match_type' in df.columns:
        df = process_match_types(df, asset_type, source)
    
    # Sort by time
    if 'time' in df.columns:
        df = df.sort_values('time')

    # Reset_index
    df = df.reset_index(drop=True)
    
    # Apply data types
    dtype_without_time = {k: v for k, v in dtype_map.items() if k != 'time' and k in df.columns}
    df = df.astype(dtype_without_time)
    
    # Add metadata
    df.attrs['symbol'] = symbol
    df.category = asset_type
    df.source = source
    
    return df

