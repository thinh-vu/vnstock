"""
Standardized indices, sectors, and market constants.

Provides centralized reference for indices, sectors, and market constants
used across all data sources (VCI, TCBS, MSN, etc.). This is shared
infrastructure for all data source wrappers.

All data sources (VCI, TCBS, MSN) use this module to provide a unified,
consistent interface for index and sector lookups.
"""

from typing import List, Optional, Dict
import pandas as pd
from vnstock.constants import (
    INDICES_INFO,
    INDICES_MAP,
    INDEX_GROUPS,
    SECTOR_IDS,
    EXCHANGES,
)


# =============================================================================
# INDEX INFORMATION QUERIES
# =============================================================================

def get_all_indices() -> pd.DataFrame:
    """
    Get list of all available indices as DataFrame.

    Returns:
        pd.DataFrame: Columns [symbol, name, description,
                               full_name, group, index_id, sector_id]
    """
    data = []
    for symbol, info in INDICES_INFO.items():
        row = {
            'symbol': symbol,
            'name': info['name'],
            'description': info['description'],
            'full_name': info['full_name'],
            'group': info['group'],
            'index_id': info['index_id'],
        }
        # sector_id chỉ có với sector indices
        if 'sector_id' in info:
            row['sector_id'] = info['sector_id']
        data.append(row)
    return pd.DataFrame(data)


def get_index_info(symbol: str) -> Optional[Dict]:
    """
    Get complete information for an index.

    Args:
        symbol: Index symbol (e.g., 'VN30', 'VNIT')

    Returns:
        Optional[Dict]: Index info dict or None if not found
    """
    return INDICES_INFO.get(symbol.upper())


def get_index_id(symbol: str) -> Optional[int]:
    """
    Get index ID by symbol (for backward compatibility).

    Args:
        symbol: Index symbol (e.g., 'VN30', 'VNIT')

    Returns:
        Optional[int]: Index ID if found, None otherwise
    """
    return INDICES_MAP.get(symbol.upper())


def get_index_description(symbol: str) -> Optional[str]:
    """
    Get description for an index.

    Args:
        symbol: Index symbol

    Returns:
        Optional[str]: Description or None if not found
    """
    info = INDICES_INFO.get(symbol.upper())
    return info['description'] if info else None


def is_valid_index(symbol: str) -> bool:
    """
    Check if symbol is a valid index.

    Args:
        symbol: Index symbol

    Returns:
        bool: True if index exists
    """
    return symbol.upper() in INDICES_INFO


# =============================================================================
# INDEX GROUP QUERIES
# =============================================================================

def get_indices_by_group(group: str) -> Optional[pd.DataFrame]:
    """
    Get indices in a specific group.

    Args:
        group: Group name (VD: 'HOSE Indices', 'Sector Indices', etc.)

    Returns:
        pd.DataFrame: Filtered indices or None if group not found
    """
    if group not in INDEX_GROUPS:
        return None

    symbols = INDEX_GROUPS[group]
    data = []
    for symbol in symbols:
        if symbol in INDICES_INFO:
            info = INDICES_INFO[symbol]
            row = {
                'symbol': symbol,
                'name': info['name'],
                'description': info['description'],
                'full_name': info['full_name'],
                'group': info['group'],
                'index_id': info['index_id'],
            }
            # sector_id chỉ có với sector indices
            if 'sector_id' in info:
                row['sector_id'] = info['sector_id']
            data.append(row)
    return pd.DataFrame(data) if data else None


def get_all_index_groups() -> List[str]:
    """
    Get all available index groups.

    Returns:
        List[str]: Group names
    """
    return list(INDEX_GROUPS.keys())


def get_indices_symbols_by_group(group: str) -> Optional[List[str]]:
    """
    Get symbols in a specific group as list.

    Args:
        group: Group name

    Returns:
        Optional[List[str]]: List of symbols or None
    """
    return INDEX_GROUPS.get(group)


# =============================================================================
# SECTOR QUERIES
# =============================================================================

def get_sector_name(sector_id: int) -> Optional[str]:
    """
    Get sector name by ID.

    Args:
        sector_id: Sector ID

    Returns:
        Optional[str]: Sector name or None if not found
    """
    return SECTOR_IDS.get(sector_id)


def get_all_sectors() -> pd.DataFrame:
    """
    Get all sectors as DataFrame.

    Returns:
        pd.DataFrame: Columns [sector_id, name]
    """
    data = [
        {'sector_id': sid, 'name': sname}
        for sid, sname in SECTOR_IDS.items()
    ]
    return pd.DataFrame(data)


# =============================================================================
# EXCHANGE QUERIES
# =============================================================================

def get_all_exchanges() -> List[str]:
    """
    Get all stock exchange codes.

    Returns:
        List[str]: Exchange codes (HOSE, HNX, UPCOM)
    """
    return list(EXCHANGES.keys())


def get_exchange_name(code: str) -> Optional[str]:
    """
    Get exchange full name by code.

    Args:
        code: Exchange code (HOSE, HNX, UPCOM)

    Returns:
        Optional[str]: Exchange name or None if not found
    """
    return EXCHANGES.get(code.upper())
