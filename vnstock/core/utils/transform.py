"""Data transformation utilities for vnstock data sources."""

import re
import pytz
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta, time
from vnstock.core.utils.parser import localize_timestamp
from vnstock.core.utils.logger import get_logger

logger = get_logger(__name__)

# Vietnam timezone
vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')

# ==== Utils functions for data transformation ====

def clean_numeric_string(s: Any) -> Any:
    """
    Loại bỏ dấu phân nhóm (',' hoặc NBSP), chuẩn hoá dấu thập phân về '.'
    """
    if not isinstance(s, str):
        return s
    s = s.replace('\u00A0', '').replace(',', '')
    # Nếu chỉ có một dấu ',' (nghĩa decimal), chuyển thành '.'
    if s.count('.') == 0 and s.count(',') == 1:
        s = s.replace(',', '.')
    return s.strip()

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
                # Morning session: Find transactions around 9:15 AM (9:13-9:17)
                morning_mask = unknown_mask & (df['time'].dt.hour == 9) & (df['time'].dt.minute >= 13) & (df['time'].dt.minute <= 17)
                morning_indices = df[morning_mask].index
                
                # Afternoon session: Find transactions around 2:45 PM (14:43-14:47)
                afternoon_mask = unknown_mask & (df['time'].dt.hour == 14) & (df['time'].dt.minute >= 43) & (df['time'].dt.minute <= 47)
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

def intraday_to_df(
    data: List[Dict[str, Any]],
    column_map: Dict[str, str],
    dtype_map: Dict[str, str],
    symbol: str,
    asset_type: str,
    source: str
) -> pd.DataFrame:
    """
    Convert intraday trading data to standardized DataFrame format,
    với:
      - Tiền xử lý chuỗi số cho price/volume
      - Map scale dựa trên source (không hardcode /1000)
      - Kiểm soát NaN, rounding volume an toàn
      - Xử lý time, match_type như trước
    """
    # --- Early exit ---
    if not data:
        empty_df = pd.DataFrame(columns=list(column_map.values()))
        empty_df.attrs['symbol'] = symbol
        empty_df.category = asset_type
        empty_df.source = source
        return empty_df

    df = pd.DataFrame(data)

    # --- Chọn & rename columns ---
    available = [c for c in column_map if c in df.columns]
    if not available:
        raise ValueError(f"Expected columns {list(column_map)} not found, got {df.columns.tolist()}")
    df = df[available].rename(columns={k: column_map[k] for k in available})

    # --- Làm sạch & chuyển numeric ---
    for col in ('price', 'volume'):
        if col in df.columns:
            # Tiền xử lý chuỗi
            df[col] = df[col].map(clean_numeric_string)
            # Chuyển sang float, lỗi thành NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            n_bad = df[col].isna().sum()
            if n_bad:
                print(f"[Warning] {n_bad} giá trị ở '{col}' không parse được, chuyển thành NaN")

    # --- Scale price theo source ---
    scale_map = {'VCI': 1000, 'MAS': 1000}
    scale = scale_map.get(source, 1)
    if 'price' in df.columns:
        df['price'] = df['price'] / scale

    # --- Volume: round & cast int ---
    if 'volume' in df.columns:
        vol = df['volume'].fillna(0)
        # Kiểm tra nếu có decimal
        mask = (vol % 1 != 0)
        if mask.any():
            print(f"[Info] {int(mask.sum())} giá trị volume có decimal, sẽ làm tròn")
        df['volume'] = vol.round().astype(int)

    # --- Xử lý cột time như trước ---
    if 'time' in df.columns:
        trading_date = get_trading_date()

        if source == 'VCI':
            df['time'] = localize_timestamp(df['time'].astype(int), unit='s')
        elif source == 'MAS':
            df['time'] = localize_timestamp(df['time'].astype(int), unit='ms')
            df['time'] = df['time'].dt.floor('s')
        else:  # TCBS
            sample = str(df['time'].iloc[0]) if not df.empty else ''
            if ':' in sample and len(sample) <= 8:
                df['time'] = df['time'].apply(
                    lambda x: datetime.combine(
                        trading_date,
                        datetime.strptime(x, '%H:%M:%S').time()
                    ) if isinstance(x, str) and ':' in x else pd.NaT
                )
                df['time'] = localize_timestamp(df['time'], return_string=False)
            else:
                df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
                if df['time'].dt.tz is None:
                    df['time'] = localize_timestamp(df['time'], return_string=False)

    # --- Process match types như bạn đã định nghĩa ---
    if 'match_type' in df.columns:
        df = process_match_types(df, asset_type, source)

    # --- Sort, reset index & apply dtype ---
    if 'time' in df.columns:
        df = df.sort_values('time')
    df = df.reset_index(drop=True)

    # Áp dtype_map (không tính time)
    type_map = {k: v for k, v in dtype_map.items() if k in df.columns and k != 'time'}
    if type_map:
        df = df.astype(type_map)

    # --- Metadata ---
    df.attrs['symbol'] = symbol
    df.category = asset_type
    df.source = source

    return df

def replace_in_column_names(df, old_text, new_text, regex=False):
    """
    Replace text in column names.
    
    Parameters:
        df (pd.DataFrame): DataFrame with column names to modify
        old_text (str): Text to be replaced
        new_text (str): New text to replace with
        regex (bool): Whether to treat old_text as a regular expression pattern
        
    Returns:
        pd.DataFrame: DataFrame with modified column names
    """
    df.columns = df.columns.str.replace(old_text, new_text, regex=regex)
    return df

def flatten_hierarchical_index(df, separator="_", text_replacements=None, handle_duplicates=True, 
                              drop_levels=None, keep_levels=None):
    """
    Flatten hierarchical (multi-level) column indexes into a single level for easier Excel export.
    
    Parameters:
        df (pd.DataFrame): DataFrame with hierarchical index to flatten
        separator (str): Character(s) to use when joining index levels
        text_replacements (dict): Dictionary of text replacements to apply to column names
                                 {old_text: new_text}
        handle_duplicates (bool): Whether to handle duplicate column names by adding '_' prefix
        drop_levels (list or int): Levels to drop (by position); can be a list of indices or a single index.
                                   To drop highest level, use drop_levels=0
        keep_levels (list or int): Levels to keep (by position); can be a list of indices or a single index.
                                   This takes precedence over drop_levels if both are specified.
    
    Returns:
        pd.DataFrame: DataFrame with flattened column index
    """
    # Make a copy to avoid modifying the original DataFrame
    result_df = df.copy()
    
    # If the DataFrame doesn't have a hierarchical index, just return it
    if not isinstance(result_df.columns, pd.MultiIndex):
        return result_df
    
    # Get the number of levels in the MultiIndex
    num_levels = result_df.columns.nlevels
    
    # Convert to flat index (list of tuples where each tuple contains all level values for a column)
    flat_cols = result_df.columns.to_flat_index()
    
    # Determine which levels to include based on parameters
    if keep_levels is not None:
        # Convert single value to list if necessary
        if isinstance(keep_levels, int):
            keep_levels = [keep_levels]
        # Create a list of level indices to keep
        level_indices = keep_levels
    elif drop_levels is not None:
        # Convert single value to list if necessary
        if isinstance(drop_levels, int):
            drop_levels = [drop_levels]
        # Create a list of all level indices except those to drop
        level_indices = [i for i in range(num_levels) if i not in drop_levels]
    else:
        # If no levels specified to keep or drop, include all levels
        level_indices = list(range(num_levels))
    
    # Apply text replacements if provided
    if text_replacements:
        # Process each column name tuple
        processed_cols = []
        for col in flat_cols:
            # Process each level in the column
            processed_col = []
            for i, level in enumerate(col):
                level_str = str(level)
                # Apply all text replacements to this level
                for old_text, new_text in text_replacements.items():
                    level_str = level_str.replace(old_text, new_text)
                processed_col.append(level_str)
            processed_cols.append(tuple(processed_col))
        flat_cols = processed_cols
    
    # Join selected levels with separator, ignoring empty strings
    flattened_cols = []
    for col in flat_cols:
        # Filter to only include the selected levels
        selected_levels = [str(col[i]) for i in level_indices if i < len(col) and col[i] != '']
        # Join the levels with the separator
        flattened_cols.append(separator.join(selected_levels))
    
    # Assign the flattened column names
    result_df.columns = flattened_cols
    
    # Handle duplicated column names
    if handle_duplicates:
        duplicated_cols = result_df.columns[result_df.columns.duplicated()].tolist()
        if duplicated_cols:
            for col in duplicated_cols:
                # Find all occurrences of the duplicated column
                col_indices = [i for i, x in enumerate(result_df.columns) if x == col]
                # Keep the first occurrence unchanged, prefix others with '_'
                for idx in col_indices[1:]:
                    # Create a new column name with '_' prefix
                    new_col_name = f"_{result_df.columns[idx]}"
                    # Rename the column in-place
                    result_df.rename(columns={result_df.columns[idx]: new_col_name}, inplace=True)
    
    return result_df

# ==== Process nested JSON data to DataFrame ====

def flatten_dict_to_df(data: Dict[str, Any], nested_key: str = 'financialRatio') -> pd.DataFrame:
    """
    Flatten nested dictionary data into a pandas DataFrame.
    
    Extracts all fields from input dictionary, including nested fields from a specified
    structure, preserving all underlying data while removing the top-level label.
    
    Parameters:
    -----------
    data : Dict[str, Any]
        Dictionary/JSON data containing nested structures
    nested_key : str, optional
        Key of the nested structure to flatten (default: 'financialRatio')
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with a single row containing all flattened fields
    """
    # Copy top-level data excluding the nested structure
    result = {k: v for k, v in data.items() if k != nested_key}
    
    # Process nested structure if it exists
    if nested_key in data:
        nested_data = data[nested_key]
        
        # Handle key conflicts between top level and nested data
        for key, value in nested_data.items():
            if key in result:
                result[f"{nested_key}_{key}"] = value  # Add prefix to avoid conflicts
            else:
                result[key] = value  # Add directly if no conflict
    
    # Flatten any remaining nested structures
    flat_data = {}
    _flatten_nested(result, flat_data)
    
    # Return as DataFrame
    return pd.DataFrame([flat_data])

def flatten_list_to_df(data_list, nested_key='subOrListingInfo'):
    """
    Flatten a list of dictionaries with a nested key into a pandas DataFrame.
    
    Parameters:
    -----------
    data_list : list
        List of dictionaries where each dictionary contains a nested structure
    nested_key : str, optional
        Key in each dictionary containing the nested data (default: 'subOrListingInfo')
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with all fields flattened (nested data combined with top-level data)
        
    Example:
    --------
    >>> data = [
    ...     {'id': '21592027', 'organCode': 'VNM', 
    ...      'subOrListingInfo': {'enOrganName': 'Apis Corporation'}},
    ...     {'id': '21592028', 'organCode': 'VNM',
    ...      'subOrListingInfo': {'enOrganName': 'Asia Coconut Processing JSC'}}
    ... ]
    >>> flatten_list_to_df(data)
    """
    import pandas as pd
    
    # Initialize an empty list to store flattened rows
    flattened_rows = []
    
    for item in data_list:
        # Create a copy of the item to avoid modifying the original
        item_copy = item.copy()
        
        # Extract and remove the nested data
        nested_data = item_copy.pop(nested_key, {})
        
        # Merge top-level data with nested data
        flattened_row = {**item_copy, **nested_data}
        flattened_rows.append(flattened_row)
    
    # Convert the list of flattened rows to a DataFrame
    return pd.DataFrame(flattened_rows)

def _flatten_nested(obj: Any, output: Dict[str, Any], prefix: str = '') -> None:
    """
    Recursively flatten nested structures into a single-level dictionary.
    
    Parameters:
    -----------
    obj : Any
        Object to flatten (dict, list, or primitive value)
    output : Dict[str, Any]
        Dictionary where flattened data will be stored
    prefix : str, optional
        Current key prefix for nested structures
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{prefix}_{k}" if prefix else k
            if isinstance(v, (dict, list)) and v:
                _flatten_nested(v, output, new_key)
            else:
                output[new_key] = v
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key = f"{prefix}_{i}" if prefix else str(i)
            if isinstance(item, (dict, list)) and item:
                _flatten_nested(item, output, new_key)
            else:
                output[new_key] = item
    else:
        output[prefix] = obj

def clean_html_dict(data: Dict[str, Any], html_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Convert HTML to plain text in dictionary values.
    
    Processes string values containing HTML and converts them to readable plain text
    while preserving basic formatting like lists and line breaks.
    
    Parameters:
    -----------
    data : Dict[str, Any]
        Dictionary containing HTML content in values
    html_keys : List[str], optional
        Keys to process as HTML; if None, auto-detects HTML content
        
    Returns:
    --------
    Dict[str, Any]
        Dictionary with HTML content converted to plain text
    """
    if not isinstance(data, dict):
        return data
    
    result = data.copy()
    
    # Auto-detect HTML keys if not specified
    if html_keys is None:
        html_keys = [k for k, v in data.items() 
                    if isinstance(v, str) and '<' in v and '>' in v]
    
    # Process HTML in identified keys
    for key in html_keys:
        if key in result and isinstance(result[key], str):
            try:
                # Parse and clean HTML
                soup = BeautifulSoup(result[key], 'html.parser')
                
                # Preserve line breaks
                for br in soup.find_all('br'):
                    br.replace_with('\n')
                
                # Format list items
                for li in soup.find_all('li'):
                    li.insert_before('- ')
                
                # Clean and format text
                text = soup.get_text()
                text = ' '.join(text.split())
                text = text.replace('- ', '\n- ')  # Preserve list formatting
                
                result[key] = text
            except:
                pass  # Keep original if processing fails
    
    return result

# ==== Data presentation and readability ====

def reorder_cols(df, cols, position='first'):
    """
    Move specified columns to the first or last position in a DataFrame.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame whose columns to reorder
    cols : str or list
        Column name(s) to move
    position : str, optional
        Target position: 'first' or 'last' (default: 'first')
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with reordered columns
        
    Examples:
    ---------
    # Move 'symbol' to the first position
    df = reorder_cols(df, 'symbol')
    
    # Move multiple columns to the end
    df = reorder_cols(df, ['created_at', 'updated_at'], 'last')
    """
    # Convert single column to list
    if isinstance(cols, str):
        cols = [cols]
    
    # Filter to include only columns that exist
    move_cols = [col for col in cols if col in df.columns]
    
    if not move_cols:
        return df  # No valid columns to move
    
    # Get remaining columns
    other_cols = [col for col in df.columns if col not in move_cols]
    
    # Create new column order based on position
    if position.lower() == 'first':
        new_order = move_cols + other_cols
    elif position.lower() == 'last':
        new_order = other_cols + move_cols
    else:
        raise ValueError("Position must be 'first' or 'last'")
    
    # Return reordered DataFrame
    return df[new_order]

def drop_cols_by_pattern(df, patterns, regex=True, case_sensitive=False):
    """
    Drop columns from DataFrame where names match specified pattern(s).
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to filter
    patterns : str or list
        Pattern(s) to match in column names
    regex : bool, optional
        Whether to treat patterns as regex (default: True)
    case_sensitive : bool, optional
        Whether matching should be case-sensitive (default: False)
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with matching columns removed
        
    Examples:
    ---------
    # Drop columns containing 'date'
    df = drop_cols_by_pattern(df, 'date', regex=False)
    
    # Drop columns ending with '_id' or '_key'
    df = drop_cols_by_pattern(df, ['_id$', '_key$'])
    """
    import re
    
    # Convert single pattern to list
    if isinstance(patterns, str):
        patterns = [patterns]
    
    # Identify columns to drop
    cols_to_drop = []
    
    for col in df.columns:
        for pattern in patterns:
            if regex:
                flags = 0 if case_sensitive else re.IGNORECASE
                try:
                    if re.search(pattern, col, flags):
                        cols_to_drop.append(col)
                        break
                except re.error:
                    raise ValueError(f"Invalid regex pattern: {pattern}")
            else:
                if case_sensitive:
                    if pattern in col:
                        cols_to_drop.append(col)
                        break
                else:
                    if pattern.lower() in col.lower():
                        cols_to_drop.append(col)
                        break
    
    # Return DataFrame with matched columns removed
    return df.drop(columns=cols_to_drop)
