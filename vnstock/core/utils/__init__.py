"""
vnstock.core.utils - Utility functions for data processing and validation.

Public API exports for common utility operations.
"""

# Validation utilities
from .validation import (
    validate_symbol,
    validate_date_range,
    convert_to_timestamps,
    validate_interval,
    validate_pagination,
    validate_model_input,
)

# Parser utilities
from .parser import (
    parse_timestamp,
    localize_timestamp,
    get_asset_type,
    camel_to_snake,
    flatten_data,
    last_n_days,
    vn30_expand_contract,
    vn30_abbrev_contract,
)

# Transform utilities
from .transform import (
    clean_numeric_string,
    get_trading_date,
    ohlc_to_df,
    intraday_to_df,
    replace_in_column_names,
    flatten_hierarchical_index,
    flatten_dict_to_df,
    flatten_list_to_df,
    clean_html_dict,
    reorder_cols,
    drop_cols_by_pattern,
)

# Logging
from .logger import get_logger, advanced_logger

# Client utilities
from .client import (
    send_request,
    send_direct_request,
    send_proxy_request,
    send_hf_proxy_request,
    ProxyMode,
    RequestMode,
    ProxyConfig,
)

# Environment utilities
from .env import (
    get_platform,
    get_hosting_service,
    get_package_path,
    id_valid,
    get_username,
    get_cwd,
    get_path_delimiter,
)

__all__ = [
    # Validation
    'validate_symbol',
    'validate_date_range',
    'convert_to_timestamps',
    'validate_interval',
    'validate_pagination',
    'validate_model_input',
    # Parser
    'parse_timestamp',
    'localize_timestamp',
    'get_asset_type',
    'camel_to_snake',
    'flatten_data',
    'last_n_days',
    'vn30_expand_contract',
    'vn30_abbrev_contract',
    # Transform
    'clean_numeric_string',
    'get_trading_date',
    'ohlc_to_df',
    'intraday_to_df',
    'replace_in_column_names',
    'flatten_hierarchical_index',
    'flatten_dict_to_df',
    'flatten_list_to_df',
    'clean_html_dict',
    'reorder_cols',
    'drop_cols_by_pattern',
    # Logging
    'get_logger',
    'advanced_logger',
    # Client
    'send_request',
    'send_direct_request',
    'send_proxy_request',
    'send_hf_proxy_request',
    'ProxyMode',
    'RequestMode',
    'ProxyConfig',
    # Environment
    'get_platform',
    'get_hosting_service',
    'get_package_path',
    'id_valid',
    'get_username',
    'get_cwd',
    'get_path_delimiter',
]
