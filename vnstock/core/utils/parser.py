# vnstock/core/utils/parser.py

import re
import unicodedata
import requests
import pandas as pd
import numpy as np
from pytz import timezone
from datetime import date, datetime, timedelta
from typing import Dict, Union, Literal, Any, Optional
from vnstock.core.utils.logger import get_logger

logger = get_logger(__name__)

# Lazy import to avoid circular import
_INDICES_INFO = None
_UA = None

def _get_indices_info():
    """Lazy load INDICES_INFO to avoid circular import."""
    global _INDICES_INFO
    if _INDICES_INFO is None:
        from vnstock.constants import INDICES_INFO as _ii
        _INDICES_INFO = _ii
    return _INDICES_INFO

def _get_ua():
    """Lazy load UA to avoid circular import."""
    global _UA
    if _UA is None:
        from vnstock.core.config.const import UA as _ua
        _UA = _ua
    return _UA

def get_asset_type(symbol: str) -> str:
    """
    Determine asset type based on provided security code.
    Supports both legacy code format and new KRX format.
    
    Parameters:
        - symbol (str): Security code or index symbol.
    
    Returns:
        - 'index' if security code is an index symbol.
        - 'stock' if security code is a stock symbol.
        - 'derivative' if security code is a futures or options contract.
        - 'bond' if security code is a government or corporate bond.
        - 'coveredWarr' if security code is a covered warrant.
    """
    symbol = symbol.upper()
    
    # Standard market indices and HOSE managed indices
    market_indices = {'VNINDEX', 'HNXINDEX', 'UPCOMINDEX', 'HNX30'}
    # Combine with indices from constants
    indices_info = _get_indices_info()
    known_indices = market_indices.union(indices_info.keys())

    if symbol in known_indices:
        return 'index'
    
    # Stock symbols (assumed to have 3 characters)
    elif len(symbol) == 3:
        return 'stock'
    
    # New KRX derivative format (e.g., 41I1F4000)
    krx_derivative_pattern = re.compile(r'^4[12][A-Z0-9]{2}[0-9A-HJ-NP-TV-W][1-9A-C]\d{3}$')
    if krx_derivative_pattern.match(symbol):
        return 'derivative'

    # VN100 derivative patterns (e.g., VN100F1M, VN100F2M, VN100F1Q, VN100F2Q)
    vn100_derivative_pattern = re.compile(r'^VN100F\d{1,2}[MQ]$')
    if vn100_derivative_pattern.match(symbol):
        return 'derivative'
    
    # For symbols that could be derivative or bond (length 7 or 9)
    elif len(symbol) in [7, 9]:
        # VN30 derivative patterns:
        fm_pattern = re.compile(r'^VN30F\d{1,2}[MQ]$')
        ym_pattern = re.compile(r'^VN30F\d{4}$')
        
        # Bond patterns:
        # Government bond: e.g., GB05F2506 or GB10F2024
        gov_bond_pattern = re.compile(r'^GB\d{2}F\d{4}$')
        # Company bond: e.g., BAB122032; exclude those starting with VN30F.
        comp_bond_pattern = re.compile(r'^(?!VN30F)[A-Z]{3}\d{6}$')
        
        if gov_bond_pattern.match(symbol) or comp_bond_pattern.match(symbol):
            return 'bond'
        elif fm_pattern.match(symbol) or ym_pattern.match(symbol):
            return 'derivative'
        else:
            raise ValueError('Invalid derivative or bond symbol. Symbol must be in format of VN30F1M, VN30F2024, GB10F2024, or for company bonds, e.g., BAB122032')
    
    # Covered warrant symbols (assumed to have 8 characters)
    elif len(symbol) == 8:
        return 'coveredWarr'
    
    else:
        raise ValueError('Invalid symbol. Your symbol format is not recognized!')

def parse_timestamp(time_value):
    """
    Convert a datetime object or a string representation of time to a Unix timestamp.
    Parameters:
        - time_value: A datetime object or a string representation of time. Supported formats are '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', and '%Y-%m-%d' or datetime object.
    """
    try:
        if isinstance(time_value, datetime):
            time_value = timezone('Asia/Ho_Chi_Minh').localize(time_value)
        elif isinstance(time_value, str):
            if ' ' in time_value and ':' in time_value.split(' ')[1]:
                try:
                    time_value = datetime.strptime(time_value, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    time_value = datetime.strptime(time_value, '%Y-%m-%d %H:%M')
            else:
                time_value = datetime.strptime(time_value, '%Y-%m-%d')
        else:
            print("Invalid input type. Supported types are datetime or string.")
            return None

        timestamp = int(time_value.timestamp())
        return timestamp
    except ValueError:
        print("Invalid timestamp format")
        return None

# Utility to convert timestamps to Vietnam timezone
def localize_timestamp (
    timestamp: Union[pd.Series, int, float, list, np.ndarray, pd.Timestamp, Any], 
    unit: Literal['s', 'ms', 'us', 'ns'] = 's',
    return_scalar: bool = False,
    return_string: bool = False,
    string_format: str = '%Y-%m-%d %H:%M:%S'
) -> Union[pd.Series, pd.Timestamp, str]:
    """
    Convert timestamp values to Vietnam timezone (UTC+7).
    
    Parameters:
        timestamp: Timestamp value(s) - can be Series, list, array, or scalar
        unit: Unit for timestamp conversion ('s' for seconds, 'ms' for milliseconds, etc.)
        return_scalar: If True and input can be treated as scalar, return a single value
        return_string: If True, return string representation(s) instead of datetime objects
        string_format: Format for datetime strings if return_string=True
        
    Returns:
        - Series of datetime objects (default)
        - Series of formatted strings (if return_string=True)
        - Single Timestamp (if return_scalar=True and input is scalar-like)
        - Formatted string (if return_scalar=True, return_string=True and input is scalar-like)
        
    Examples:
        # Convert a single timestamp (returns Series by default)
        convert_to_vietnam_time(1647851234)
        
        # Convert a single timestamp (return scalar Timestamp)
        convert_to_vietnam_time(1647851234, return_scalar=True)
        
        # Convert a single timestamp (return string)
        convert_to_vietnam_time(1647851234, return_string=True)
        
        # Convert multiple timestamps to string Series
        convert_to_vietnam_time([1647851234, 1647851235], return_string=True)
    """
    # Determine if input should be treated as a scalar value
    treat_as_scalar = False
    
    # Direct scalar types
    if np.isscalar(timestamp) or isinstance(timestamp, (pd.Timestamp, datetime)):
        treat_as_scalar = True
        timestamp_series = pd.Series([timestamp])
    # Series with one element
    elif isinstance(timestamp, pd.Series) and len(timestamp) == 1:
        treat_as_scalar = True
        timestamp_series = timestamp
    # List, array, etc. with one element
    elif hasattr(timestamp, '__len__') and len(timestamp) == 1:
        treat_as_scalar = True
        timestamp_series = pd.Series(timestamp)
    # Other cases - treat as non-scalar
    else:
        timestamp_series = pd.Series(timestamp) if not isinstance(timestamp, pd.Series) else timestamp
    
    # Convert to datetime with timezone
    dt_series = pd.to_datetime(timestamp_series, unit=unit)
    vietnam_series = dt_series.dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
    
    # Apply string formatting if requested
    if return_string:
        vietnam_series = vietnam_series.dt.strftime(string_format)
    
    # Return scalar if requested and input was scalar-like
    if return_scalar and treat_as_scalar:
        return vietnam_series.iloc[0]
    
    return vietnam_series

def get_asset_type(symbol: str) -> str:
    """
    Determine asset type based on provided security code.
    Supports both legacy code format and new KRX format.
    
    Parameters:
        - symbol (str): Security code or index symbol.
    
    Returns:
        - 'index' if security code is an index symbol.
        - 'stock' if security code is a stock symbol.
        - 'derivative' if security code is a futures or options contract.
        - 'bond' if security code is a government or corporate bond.
        - 'coveredWarr' if security code is a covered warrant.
    """
    symbol = symbol.upper()
    
    # Standard market indices and HOSE managed indices
    market_indices = {'VNINDEX', 'HNXINDEX', 'UPCOMINDEX', 'HNX30'}
    # Combine with indices from constants
    indices_info = _get_indices_info()
    known_indices = market_indices.union(indices_info.keys())

    if symbol in known_indices:
        return 'index'
    
    # Stock symbols (assumed to have 3 characters)
    elif len(symbol) == 3:
        return 'stock'
    
    # New KRX derivative format (e.g., 41I1F4000)
    krx_derivative_pattern = re.compile(r'^4[12][A-Z0-9]{2}[0-9A-HJ-NP-TV-W][1-9A-C]\d{3}$')
    if krx_derivative_pattern.match(symbol):
        return 'derivative'

    # VN100 derivative patterns (e.g., VN100F1M, VN100F2M, VN100F1Q, VN100F2Q)
    vn100_derivative_pattern = re.compile(r'^VN100F\d{1,2}[MQ]$')
    if vn100_derivative_pattern.match(symbol):
        return 'derivative'
    
    # For symbols that could be derivative or bond (length 7 or 9)
    elif len(symbol) in [7, 9]:
        # VN30 derivative patterns:
        fm_pattern = re.compile(r'^VN30F\d{1,2}[MQ]$')
        ym_pattern = re.compile(r'^VN30F\d{4}$')
        
        # Bond patterns:
        # Government bond: e.g., GB05F2506 or GB10F2024
        gov_bond_pattern = re.compile(r'^GB\d{2}F\d{4}$')
        # Company bond: e.g., BAB122032; exclude those starting with VN30F.
        comp_bond_pattern = re.compile(r'^(?!VN30F)[A-Z]{3}\d{6}$')
        
        if gov_bond_pattern.match(symbol) or comp_bond_pattern.match(symbol):
            return 'bond'
        elif fm_pattern.match(symbol) or ym_pattern.match(symbol):
            return 'derivative'
        else:
            raise ValueError('Invalid derivative or bond symbol. Symbol must be in format of VN30F1M, VN30F2024, GB10F2024, or for company bonds, e.g., BAB122032')
    
    # Covered warrant symbols (assumed to have 8 characters)
    elif len(symbol) == 8:
        return 'coveredWarr'
    
    else:
        raise ValueError('Invalid symbol. Your symbol format is not recognized!')

def camel_to_snake(name):
    """
    Convert variable name from CamelCase to snake_case.

    Parameters:
        - name (str): Variable name in CamelCase.

    Returns:
        - str: Variable name in snake_case.
    """
    str1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    output = re.sub('([a-z0-9])([A-Z])', r'\1_\2', str1).lower()
    # replace . with _
    output = output.replace('.', '_')
    return output

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                    VIETNAMESE TEXT NORMALIZATION MODULE                      ║
# ║                                                                              ║
# ║  This module provides robust Vietnamese text normalization for financial     ║
# ║  data processing, with accurate accent removal and database-friendly output.   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# Vietnamese character mapping for better accuracy
VIETNAMESE_CHAR_MAP: Dict[str, str] = {
    'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
    'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
    'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
    'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
    'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
    'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
    'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
    'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
    'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
    'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
    'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
    'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    'đ': 'd', 'Đ': 'd',
}


def remove_vietnamese_accents(text: str, use_map: bool = True) -> str:
    """
    Remove Vietnamese accents/diacritics from text.
    
    Args:
        text: Vietnamese text with diacritics
        use_map: Use predefined character map for accuracy (default: True)
        
    Returns:
        Text with accents removed
    """
    if use_map:
        # Use predefined mapping for Vietnamese characters (more accurate)
        result = []
        for char in text:
            if char.lower() in VIETNAMESE_CHAR_MAP:
                mapped = VIETNAMESE_CHAR_MAP[char.lower()]
                result.append(mapped.upper() if char.isupper() else mapped)
            else:
                result.append(char)
        return ''.join(result)
    else:
        # Fallback: Unicode normalization (may miss some Vietnamese chars)
        nfd = unicodedata.normalize('NFD', text)
        return ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')


def normalize_vietnamese_text_to_snake_case(
    text: str,
    keep_numbers: bool = True,
    max_length: Optional[int] = None,
    remove_common_words: bool = False,
    preserve_acronyms: bool = False
) -> str:
    """
    Convert Vietnamese text to ASCII-compatible snake_case identifier.
    Robust normalization for Vietnamese financial line items and field names.
    
    Args:
        text: Vietnamese or English text to normalize
        keep_numbers: Whether to keep numeric digits (default: True)
        max_length: Maximum length of output (default: None/unlimited)
        remove_common_words: Remove Vietnamese stop words like 'của', 'và', 'các' (default: False)
        preserve_acronyms: Try to preserve acronyms in uppercase before conversion
        
    Returns:
        Snake_case identifier suitable for database column names
        
    Examples:
        >>> normalize_vietnamese_text_to_snake_case("1. Doanh thu")
        'doanh_thu'
        >>> normalize_vietnamese_text_to_snake_case("Doanh thu bán hàng và cung cấp dịch vụ")
        'doanh_thu_ban_hang_va_cung_cap_dich_vu'
        >>> normalize_vietnamese_text_to_snake_case("Chi phí (2023-2024)")
        'chi_phi_2023_2024'
        >>> normalize_vietnamese_text_to_snake_case("Lợi nhuận sau thuế", remove_common_words=True)
        'loi_nhuan_sau_thue'
        >>> normalize_vietnamese_text_to_snake_case("EBITDA (Lãi trước thuế)")
        'ebitda_lai_truoc_thue'
    """
    if not text or not text.strip():
        return ""
    
    original_text = text
    
    # Step 1: Remove leading numbering patterns
    # Handle: "1.", "I.", "A.", "1.1.2.", "1)", "(1)", etc.
    text = re.sub(r'^[\dIVXivx]+(\.\d+)*[\.)]\s*', '', text)
    text = re.sub(r'^\([0-9]+\)\s*', '', text)
    text = re.sub(r'^[A-Za-z][\.)]\s*', '', text)
    
    # Step 2: Handle parenthetical content intelligently
    # Option 1: Remove content in parentheses entirely (uncomment if preferred)
    # text = re.sub(r'\([^)]*\)', '', text)
    # Option 2: Keep parenthetical content (current behavior)
    text = re.sub(r'[()]', ' ', text)
    
    # Step 3: Remove quotes, apostrophes, and other punctuation
    text = re.sub(r"['\"`''""*&%$#@!?;:,.]", '', text)
    
    # Step 4: Remove Vietnamese accents/diacritics
    text = remove_vietnamese_accents(text, use_map=True)
    
    # Step 5: Handle camelCase/PascalCase before lowercasing
    if preserve_acronyms:
        text = re.sub(r'([a-z])([A-Z])', r'\1_\2', text)
    else:
        text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)
    
    # Step 6: Convert to lowercase
    text = text.lower()
    
    # Step 7: Remove common Vietnamese stop words (optional)
    if remove_common_words:
        # Common Vietnamese words that don't add meaning to field names
        stop_words = [
            'cua', 'va', 'cac', 'cho', 'tren', 'duoi', 'trong', 'ngoai',
            'tai', 'den', 'tu', 'voi', 'ma', 'la', 'thi', 'hay', 'hoac',
            'nhung', 'moi', 'nam', 'thang', 'ngay', 'ky', 'dot', 'lan'
        ]
        # Create pattern to match whole words only
        pattern = r'\b(' + '|'.join(stop_words) + r')\b'
        text = re.sub(pattern, ' ', text)
    
    # Step 8: Replace special characters and spaces with underscores
    if keep_numbers:
        # Keep alphanumeric + spaces/hyphens/underscores
        text = re.sub(r'[^a-z0-9\s_-]', ' ', text)
    else:
        # Keep only alphabetic + spaces/hyphens/underscores
        text = re.sub(r'[^a-z\s_-]', ' ', text)
    
    # Step 9: Normalize whitespace and separators to underscores
    text = re.sub(r'[\s\-/\\]+', '_', text)
    
    # Step 10: Remove consecutive underscores
    text = re.sub(r'_+', '_', text)
    
    # Step 11: Remove leading/trailing underscores
    text = text.strip('_')
    
    # Step 12: Ensure it doesn't start with a number (invalid Python/SQL identifier)
    if text and text[0].isdigit():
        text = f"n_{text}"  # 'n' for 'number' prefix
    
    # Step 13: Apply max length constraint if specified
    if max_length and len(text) > max_length:
        text = text[:max_length].rstrip('_')
    
    # Step 14: Fallback for empty result
    if not text:
        # Try to extract at least something from original text
        fallback = re.sub(r'[^a-zA-Z0-9]', '', original_text)
        if fallback:
            text = fallback.lower()[:20]
        else:
            return ""  # Return empty string instead of 'unnamed_field'
    
    return text


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                      HELPER FUNCTIONS FOR VIETNAMESE                          ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def normalize_vietnamese_text_strict(text: str) -> str:
    """
    Strict version: Only alphabetic characters, no numbers.
    Best for database column names that must be purely alphabetic.
    
    Examples:
        >>> normalize_vietnamese_text_strict("2024 - Doanh thu thuần")
        'doanh_thu_thuan'
    """
    if not text or not text.strip():
        return ""
    
    # Remove accents
    text = remove_vietnamese_accents(text)
    
    # Remove all non-alphabetic characters
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Convert to lowercase and normalize spaces
    text = text.lower()
    text = re.sub(r'\s+', '_', text)
    text = re.sub(r'_+', '_', text)
    text = text.strip('_')
    
    return text or "unnamed_field"


def batch_normalize_vietnamese_fields(
    texts: list[str],
    **kwargs
) -> Dict[str, str]:
    """
    Batch normalize multiple Vietnamese texts with collision detection.
    
    Args:
        texts: List of Vietnamese texts to normalize
        **kwargs: Arguments to pass to normalize_vietnamese_text_to_snake_case
        
    Returns:
        Dictionary mapping original text to normalized snake_case
        
    Examples:
        >>> batch_normalize_vietnamese_fields(["Doanh thu", "Doanh thu thuần"])
        {'Doanh thu': 'doanh_thu', 'Doanh thu thuần': 'doanh_thu_thuan'}
    """
    result = {}
    seen = {}
    
    for text in texts:
        normalized = normalize_vietnamese_text_to_snake_case(text, **kwargs)
        
        # Handle collisions by appending counter
        if normalized in seen:
            counter = 2
            base_normalized = normalized
            while normalized in seen:
                normalized = f"{base_normalized}_{counter}"
                counter += 1
        
        result[text] = normalized
        seen[normalized] = text
    
    return result

def normalize_english_text_to_snake_case(
    text: str,
    keep_numbers: bool = True,
    max_length: Optional[int] = None,
    preserve_acronyms: bool = False,
    preserve_hierarchy: bool = False
) -> str:
    """
    Convert English text to snake_case identifier with robust normalization.
    
    Args:
        text: English text to normalize
        keep_numbers: Whether to keep numeric digits (default: True)
        max_length: Maximum length of output (default: None/unlimited)
        preserve_acronyms: Try to preserve acronyms like "API" -> "api" instead of breaking them
        preserve_hierarchy: Preserve numbering prefixes for hierarchical structure (default: False)
        
    Returns:
        Snake_case identifier suitable for database column names
        
    Examples:
        >>> normalize_english_text_to_snake_case("1. Revenue")
        'revenue'
        >>> normalize_english_text_to_snake_case("1. Revenue", preserve_hierarchy=True)
        '1.revenue'
        >>> normalize_english_text_to_snake_case("A. ASSETS")
        'assets'
        >>> normalize_english_text_to_snake_case("A. ASSETS", preserve_hierarchy=True)
        'a.assets'
        >>> normalize_english_text_to_snake_case("Cash & cash equivalents")
        'cash_and_cash_equivalents'
        >>> normalize_english_text_to_snake_case("Shareholders' equity")
        'shareholders_equity'
    """
    if not text or not text.strip():
        return ""
    
    original_text = text
    
    # Step 1: Extract hierarchy prefix if preservation is enabled
    hierarchy_prefix = ""
    if preserve_hierarchy:
        # Extract numbering patterns: "1.", "I.", "A.", "1.1.2", etc.
        hierarchy_match = re.match(r'^([\dIVXivx]+(\.\d+)*|[A-Za-z])\.\s*', text)
        if hierarchy_match:
            hierarchy_prefix = hierarchy_match.group(1).lower() + '.'
            text = text[len(hierarchy_match.group(0)):]  # Remove the prefix from text
    
    # Step 2: Normalize unicode (handle any accented characters)
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Step 3: Remove any remaining numbering patterns (only if not preserving hierarchy)
    if not preserve_hierarchy:
        text = re.sub(r'^\d+(\.\d+)*\.\s*', '', text)  # Handle 1., 1.1., 1.1.2., etc.
        text = re.sub(r'^[IVXivx]+(\.\d+)*\.\s*', '', text)  # Handle Roman numerals
        text = re.sub(r'^[A-Za-z]\.\s*', '', text)  # Handle A., B., etc.
    
    # Step 4: Convert to lowercase BEFORE processing special characters
    text = text.lower()
    
    # Step 5: Replace & with 'and' for better readability (handle spaces properly)
    text = re.sub(r'\s*&\s*', ' and ', text)
    text = re.sub(r'^&', 'and ', text)  # Handle & at start
    text = re.sub(r'&$', ' and', text)  # Handle & at end
    
    # Step 6: Remove apostrophes and quotes completely (BEFORE other processing)
    text = re.sub(r"['\"`]", '', text)
    
    # Step 7: Handle camelCase/PascalCase by inserting underscores
    if preserve_acronyms:
        text = re.sub(r'([a-z])([A-Z])', r'\1_\2', text)
        text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', text)
    else:
        text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)
        text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', text)
    
    # Step 8: Replace special characters with spaces (keep alphanumeric, spaces, hyphens)
    if keep_numbers:
        text = re.sub(r'[^a-z0-9\s_-]', ' ', text)
    else:
        text = re.sub(r'[^a-z\s_-]', ' ', text)
    
    # Step 9: Normalize whitespace and separators to underscores
    text = re.sub(r'[\s\-/\\]+', '_', text)
    
    # Step 10: Remove consecutive underscores
    text = re.sub(r'_+', '_', text)
    
    # Step 11: Remove leading/trailing underscores
    text = text.strip('_')
    
    # Step 12: Combine hierarchy prefix with normalized text
    if hierarchy_prefix and text:
        text = hierarchy_prefix + text
    
    # Step 13: Ensure it doesn't start with a number (invalid identifier)
    if text and text[0].isdigit():
        text = f"n_{text}"
    
    # Step 14: Apply max length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length].rstrip('_')
    
    # Step 15: Fallback for empty result - extract meaningful part from original
    if not text:
        fallback = re.sub(r'[^a-zA-Z0-9]', '', original_text)
        if fallback:
            text = fallback.lower()[:20]
        else:
            return ""  # Return empty string instead of 'unnamed_field'
    
    return text


def normalize_vietnamese_text_to_snake_case(
    text: str,
    keep_numbers: bool = True,
    max_length: Optional[int] = None,
    remove_common_words: bool = False,
    preserve_acronyms: bool = False,
    preserve_hierarchy: bool = False
) -> str:
    """
    Convert Vietnamese text to ASCII-compatible snake_case identifier.
    Robust normalization for Vietnamese financial line items and field names.
    
    Args:
        text: Vietnamese or English text to normalize
        keep_numbers: Whether to keep numeric digits (default: True)
        max_length: Maximum length of output (default: None/unlimited)
        remove_common_words: Remove Vietnamese stop words like 'của', 'và', 'các' (default: False)
        preserve_acronyms: Try to preserve acronyms in uppercase before conversion
        preserve_hierarchy: Preserve numbering prefixes for hierarchical structure (default: False)
        
    Returns:
        Snake_case identifier suitable for database column names
        
    Examples:
        >>> normalize_vietnamese_text_to_snake_case("1. Doanh thu")
        'doanh_thu'
        >>> normalize_vietnamese_text_to_snake_case("1. Doanh thu", preserve_hierarchy=True)
        '1.doanh_thu'
        >>> normalize_vietnamese_text_to_snake_case("A. TÀI SẢN")
        'tai_san'
        >>> normalize_vietnamese_text_to_snake_case("A. TÀI SẢN", preserve_hierarchy=True)
        'a.tai_san'
        >>> normalize_vietnamese_text_to_snake_case("Doanh thu bán hàng và cung cấp dịch vụ")
        'doanh_thu_ban_hang_va_cung_cap_dich_vu'
        >>> normalize_vietnamese_text_to_snake_case("Chi phí (2023-2024)")
        'chi_phi_2023_2024'
        >>> normalize_vietnamese_text_to_snake_case("Lợi nhuận sau thuế", remove_common_words=True)
        'loi_nhuan_sau_thue'
        >>> normalize_vietnamese_text_to_snake_case("EBITDA (Lãi trước thuế)")
        'ebitda_lai_truoc_thue'
    """
    if not text or not text.strip():
        return ""
    
    original_text = text
    
    # Step 1: Extract hierarchy prefix if preservation is enabled
    hierarchy_prefix = ""
    if preserve_hierarchy:
        # Extract numbering patterns: "1.", "I.", "A.", "1.1.2", etc.
        hierarchy_match = re.match(r'^([\dIVXivx]+(\.\d+)*|[A-Za-z])\.\s*', text)
        if hierarchy_match:
            hierarchy_prefix = hierarchy_match.group(1).lower() + '.'
            text = text[len(hierarchy_match.group(0)):]  # Remove the prefix from text
    
    # Step 2: Remove leading numbering patterns (only if not preserving hierarchy)
    if not preserve_hierarchy:
        # Handle: "1.", "I.", "A.", "1.1.2.", "1)", "(1)", etc.
        text = re.sub(r'^[\dIVXivx]+(\.\d+)*[\.)]\s*', '', text)
        text = re.sub(r'^\([0-9]+\)\s*', '', text)
        text = re.sub(r'^[A-Za-z][\.)]\s*', '', text)
    
    # Step 3: Handle parenthetical content intelligently
    # Option 1: Remove content in parentheses entirely (uncomment if preferred)
    # text = re.sub(r'\([^)]*\)', '', text)
    # Option 2: Keep parenthetical content (current behavior)
    text = re.sub(r'[()]', ' ', text)
    
    # Step 4: Remove quotes, apostrophes, and other punctuation
    text = re.sub(r"['\"`''""*&%$#@!?;:,.]", '', text)
    
    # Step 5: Remove Vietnamese accents/diacritics
    text = remove_vietnamese_accents(text, use_map=True)
    
    # Step 6: Handle camelCase/PascalCase before lowercasing
    if preserve_acronyms:
        text = re.sub(r'([a-z])([A-Z])', r'\1_\2', text)
        # Also handle consecutive uppercase letters followed by lowercase (e.g., XMLHttp)
        text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', text)
    else:
        text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)
        # Also handle consecutive uppercase letters followed by lowercase (e.g., XMLHttp)
        text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', text)
    
    # Step 7: Convert to lowercase
    text = text.lower()
    
    # Step 8: Remove common Vietnamese stop words (optional)
    if remove_common_words:
        # Common Vietnamese words that don't add meaning to field names
        stop_words = [
            'cua', 'va', 'cac', 'cho', 'tren', 'duoi', 'trong', 'ngoai',
            'tai', 'den', 'tu', 'voi', 'ma', 'la', 'thi', 'hay', 'hoac',
            'nhung', 'moi', 'nam', 'thang', 'ngay', 'ky', 'dot', 'lan'
        ]
        # Create pattern to match whole words only
        pattern = r'\b(' + '|'.join(stop_words) + r')\b'
        text = re.sub(pattern, ' ', text)
    
    # Step 9: Replace special characters and spaces with underscores
    if keep_numbers:
        # Keep alphanumeric + spaces/hyphens/underscores
        text = re.sub(r'[^a-z0-9\s_-]', ' ', text)
    else:
        # Keep only alphabetic + spaces/hyphens/underscores
        text = re.sub(r'[^a-z\s_-]', ' ', text)
    
    # Step 10: Normalize whitespace and separators to underscores
    text = re.sub(r'[\s\-/\\]+', '_', text)
    
    # Step 11: Remove consecutive underscores
    text = re.sub(r'_+', '_', text)
    
    # Step 12: Remove leading/trailing underscores
    text = text.strip('_')
    
    # Step 13: Combine hierarchy prefix with normalized text
    if hierarchy_prefix and text:
        text = hierarchy_prefix + text
    
    # Step 14: Ensure it doesn't start with a number (invalid Python/SQL identifier)
    if text and text[0].isdigit():
        text = f"n_{text}"  # 'n' for 'number' prefix
    
    # Step 15: Apply max length constraint if specified
    if max_length and len(text) > max_length:
        text = text[:max_length].rstrip('_')
    
    # Step 16: Fallback for empty result
    if not text:
        # Try to extract at least something from original text
        fallback = re.sub(r'[^a-zA-Z0-9]', '', original_text)
        if fallback:
            text = fallback.lower()[:20]
        else:
            return ""  # Return empty string instead of 'unnamed_field'
    
    return text


def normalize_text_to_snake_case_strict(text: str) -> str:
    """
    Strict version: Only keeps alphabetic characters.
    Best for database column names that should be purely alphabetic.
    """
    if not text or not text.strip():
        return ""
    
    # Normalize unicode
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Remove all non-alphabetic characters except spaces
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Convert to lowercase and replace spaces with underscores
    text = text.lower()
    text = re.sub(r'\s+', '_', text)
    
    # Remove consecutive underscores
    text = re.sub(r'_+', '_', text)
    
    # Remove leading/trailing underscores
    text = text.strip('_')
    
    return text or "unnamed_field"


def is_valid_identifier(name: str) -> bool:
    """Check if string is a valid Python/SQL identifier."""
    if not name:
        return False
    return name.isidentifier() and not name[0].isdigit()


def flatten_data(json_data, parent_key='', sep='_'):
    """
    Flatten JSON data into standard dict format.

    Parameters:
        - json_data: JSON data returned from API.
        - parent_key: Parent key of JSON data.
        - sep: Separator character between keys.
    """
    items = []
    for k, v in json_data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_data(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def last_n_days(n):
    """
    Return a date value in YYYY-MM-DD format for last n days. If n = 0, return today's date.
    """
    date_value = (datetime.today() - timedelta(days=n)).strftime('%Y-%m-%d')
    return date_value
    
def decd(byte_data):
    from cryptography.fernet import Fernet
    import base64
    ua = _get_ua()
    kb = ua['Chrome'].replace(' ', '').ljust(32)[:32].encode('utf-8')
    kb64 = base64.urlsafe_b64encode(kb)
    cipher = Fernet(kb64)
    return cipher.decrypt(byte_data).decode('utf-8')

# VN30 Future contract parser

_QUARTER_MONTHS = [3, 6, 9, 12]

def vn30_expand_contract(abbrev: str, today: date) -> str:
    """
    Convert a VN30 futures abbreviation (e.g. 'VN30F2M') into its full code 'VN30FYYMM'.
    
    Parameters
    ----------
    abbrev : str
        Short code in format 'VN30F<n><M|Q>', where n is 1–9.
    today : datetime.date
        Reference date used to determine the year and month.

    Returns
    -------
    str
        Full contract code, e.g. 'VN30F2506'.

    Raises
    ------
    TypeError
        If inputs are not of expected types.
    ValueError
        If the abbreviation format is invalid or out of supported range.
    """
    if not isinstance(abbrev, str):
        raise TypeError(f"Expected abbrev as str, got {type(abbrev).__name__}")
    if not isinstance(today, date):
        raise TypeError(f"Expected today as datetime.date, got {type(today).__name__}")

    m = re.match(r"^VN30F([1-9])([MQ])$", abbrev)
    if not m:
        raise ValueError(f"Invalid abbrev format: '{abbrev}'. Expect 'VN30F<n><M|Q>'")
    n, cycle = int(m.group(1)), m.group(2)

    yy = today.year % 100
    if cycle == "M":
        mm = today.month + (n - 1)
    else:  # cycle == "Q"
        future_q = [q for q in _QUARTER_MONTHS if q > today.month]
        seq = future_q + _QUARTER_MONTHS
        try:
            mm = seq[n - 1]
        except IndexError:
            raise ValueError(f"No quarterly F{n}Q from month {today.month}")

    # Adjust year rollover
    add_years = (mm - 1) // 12
    mm = ((mm - 1) % 12) + 1
    yy = (yy + add_years) % 100

    return f"VN30F{yy:02d}{mm:02d}"

def vn30_abbrev_contract(full: str, today: date) -> str:
    """
    Convert full code 'VN30FYYMM' to short form 'VN30F<n><M|Q>'.
    Logic: any quarter‐month (03,06,09,12) → Q; else → M.
    """
    if not isinstance(full, str):
        raise TypeError(f"Expected full as str, got {type(full).__name__}")
    if not isinstance(today, date):
        raise TypeError(f"Expected today as datetime.date, got {type(today).__name__}")

    m = re.match(r"^VN30F(\d{2})(\d{2})$", full)
    if not m:
        raise ValueError(f"Invalid full format: '{full}'. Expect 'VN30FYYMM'")
    yy, mm = int(m.group(1)), int(m.group(2))

    # Rebuild the target year/month as a date
    century = today.year - (today.year % 100)
    year = century + yy
    if mm < today.month:
        year += 100
    target = date(year, mm, 1)

    # How many months ahead is it?
    delta = (target.year - today.year) * 12 + (target.month - today.month)
    if delta < 0:
        raise ValueError("Target contract is before today's date.")

    # ALWAYS use Q if it's a standard quarter month:
    if mm in _QUARTER_MONTHS:
        # Build the sequence of upcoming quarter‐months from today
        future_q = [q for q in _QUARTER_MONTHS if q > today.month]
        seq = future_q + _QUARTER_MONTHS
        try:
            n = seq.index(mm) + 1
        except ValueError:
            raise ValueError(f"Cannot determine quarterly sequence for month {mm}")
        cycle = 'Q'
    else:
        # Otherwise, simple “n months ahead” → M
        n = delta + 1
        cycle = 'M'

    if not (1 <= n <= 9):
        raise ValueError(f"Sequence number {n} out of supported range.")

    return f"VN30F{n}{cycle}"

def convert_time_flexible(
    time_value: Optional[Union[str, int, float]],
    time_format: Optional[str] = None,
    to_iso: bool = False,
    output_format: str = '%Y-%m-%d %H:%M:%S'
) -> Optional[Union[str, int]]:
    """
    Flexibly convert time between different formats.

    Parameters:
        - time_value: Time value input (str, int, float, or None).
          If string is epoch timestamp, will automatically convert to ISO.
        - time_format: Custom format for input string (optional).
        - to_iso: If True, convert from epoch timestamp to ISO string.
                  If False (default), convert to epoch timestamp.
        - output_format: Output string format when to_iso=True
                        (default '%Y-%m-%d %H:%M:%S').

    Returns:
        - Epoch timestamp as string if to_iso=False.
        - Datetime string if to_iso=True.
        - None if time_value is None.
    """
    if time_value is None:
        return None

    if to_iso:
        # Convert from epoch to ISO string
        if isinstance(time_value, (int, float)):
            dt = datetime.fromtimestamp(int(time_value))
            return dt.strftime(output_format)
        elif isinstance(time_value, str):
            # Try parsing epoch string
            try:
                epoch = int(float(time_value))
                dt = datetime.fromtimestamp(epoch)
                return dt.strftime(output_format)
            except (ValueError, OverflowError):
                raise ValueError(
                    f"Cannot parse epoch timestamp: {time_value}"
                )
        else:
            raise ValueError(
                f"For to_iso=True, time_value must be int, float, "
                f"or epoch string, got {type(time_value)}"
            )
    else:
        # Convert to epoch
        if isinstance(time_value, (int, float)):
            return str(int(time_value))

        if isinstance(time_value, str):
            if time_format:
                try:
                    dt = datetime.strptime(time_value, time_format)
                    return str(int(dt.timestamp()))
                except ValueError:
                    raise ValueError(
                        f"Invalid time_value format: {time_value} "
                        f"with format {time_format}"
                    )
            else:
                # Try default formats
                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                    try:
                        dt = datetime.strptime(time_value, fmt)
                        return str(int(dt.timestamp()))
                    except ValueError:
                        continue
                raise ValueError(
                    f"Cannot parse time_value: {time_value}. "
                    f"Use 'YYYY-MM-DD' or "
                    f"'YYYY-MM-DD HH:MM:SS' format or provide time_format."
                )

        raise ValueError(
            f"time_value must be str, int, or float, "
            f"got {type(time_value)}"
        )
