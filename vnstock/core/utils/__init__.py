"""
vnstock.core.utils - Utility functions for data processing and validation.

Public API exports for common utility operations.
"""

# Validation utilities
# Authentication utilities
from .auth import (
    change_api_key,
    check_status,
    register_user,
)

# Client utilities
from .client import (
    ProxyConfig,
    ProxyMode,
    RequestMode,
    send_direct_request,
    send_proxy_request,
    send_request,
)

# Pandas compatibility utilities
from .compat import (
    apply_to_dataframe,
    get_pandas_info,
    normalize_frequency_string,
    replace_newlines_in_dataframe,
    safe_resample_dataframe,
    strip_whitespace_in_dataframe,
)

# Deprecation utilities
from .deprecation import (
    DeprecationRegistry,
    deprecate_provider,
    deprecated,
    get_deprecation_info,
    list_deprecated_features,
    warn_deprecated,
)

# Environment utilities
from .env import (
    get_cwd,
    get_hosting_service,
    get_package_path,
    get_path_delimiter,
    get_platform,
    get_username,
    id_valid,
)

# Logging
from .logger import advanced_logger, get_logger

# Parser utilities
from .parser import (
    camel_to_snake,
    flatten_data,
    get_asset_type,
    last_n_days,
    localize_timestamp,
    parse_timestamp,
    vn30_abbrev_contract,
    vn30_expand_contract,
)

# Transform utilities
from .transform import (
    clean_html_dict,
    clean_numeric_string,
    drop_cols_by_pattern,
    flatten_dict_to_df,
    flatten_hierarchical_index,
    flatten_list_to_df,
    get_trading_date,
    intraday_to_df,
    ohlc_to_df,
    reorder_cols,
    replace_in_column_names,
)
from .validation import (
    convert_to_timestamps,
    validate_date_range,
    validate_interval,
    validate_model_input,
    validate_pagination,
    validate_symbol,
)

__all__ = [
    # Validation
    "validate_symbol",
    "validate_date_range",
    "convert_to_timestamps",
    "validate_interval",
    "validate_pagination",
    "validate_model_input",
    # Parser
    "parse_timestamp",
    "localize_timestamp",
    "get_asset_type",
    "camel_to_snake",
    "flatten_data",
    "last_n_days",
    "vn30_expand_contract",
    "vn30_abbrev_contract",
    # Transform
    "clean_numeric_string",
    "get_trading_date",
    "ohlc_to_df",
    "intraday_to_df",
    "replace_in_column_names",
    "flatten_hierarchical_index",
    "flatten_dict_to_df",
    "flatten_list_to_df",
    "clean_html_dict",
    "reorder_cols",
    "drop_cols_by_pattern",
    # Logging
    "get_logger",
    "advanced_logger",
    # Client
    "send_request",
    "send_direct_request",
    "send_proxy_request",
    "ProxyMode",
    "RequestMode",
    "ProxyConfig",
    # Environment
    "get_platform",
    "get_hosting_service",
    "get_package_path",
    "id_valid",
    "get_username",
    "get_cwd",
    "get_path_delimiter",
    # Deprecation
    "deprecated",
    "deprecate_provider",
    "warn_deprecated",
    "get_deprecation_info",
    "list_deprecated_features",
    "DeprecationRegistry",
    # Authentication
    "register_user",
    "change_api_key",
    "check_status",
    # Pandas compatibility
    "apply_to_dataframe",
    "replace_newlines_in_dataframe",
    "strip_whitespace_in_dataframe",
    "get_pandas_info",
    "normalize_frequency_string",
    "safe_resample_dataframe",
]
