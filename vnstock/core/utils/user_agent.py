# vnstock/vnstock/core/utils/user_agent.py

import warnings
from typing import Dict, Optional

from vnstock.core.utils.browser_profiles import USER_AGENTS

DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "DNT": "1",
    "Pragma": "no-cache",
}


# Enhanced HEADERS_MAPPING_SOURCE with support for source-specific headers
HEADERS_MAPPING_SOURCE = {
    "SSI": {
        "Referer": "https://iboard.ssi.com.vn",
        "Origin": "https://iboard.ssi.com.vn",
    },
    "VND": {
        "Referer": "https://dchart.vndirect.com.vn",
        "Origin": "https://dchart.vndirect.com.vn",
    },
    "TCBS": {
        "Referer": "https://tcinvest.tcbs.com.vn/",
        "Origin": "https://tcinvest.tcbs.com.vn/",
    },
    "VCI": {
        "Referer": "https://trading.vietcap.com.vn/",
        "Origin": "https://trading.vietcap.com.vn/",
    },
    "MSN": {"Referer": "https://www.msn.com/", "Origin": "https://www.msn.com/"},
    "FMARKET": {"Referer": "https://fmarket.vn/", "Origin": "https://fmarket.vn/"},
    "SJC": {
        "Referer": "https://sjc.com.vn/bieu-do-gia-vang",
        "Origin": "https://sjc.com.vn",
    },
}


# Supported authorization schemes
AUTH_SCHEMES = {
    "bearer": "Bearer",
    "basic": "Basic",
    "apikey": "ApiKey",
    "token": "Token",
    "jwt": "Bearer",
}


def get_authorization_header(token: str, scheme: str = "Bearer") -> Dict[str, str]:
    """
    Tạo Authorization header theo scheme cụ thể.
    Create Authorization header according to specific scheme.

    Args:
        token (str): Token hoặc credentials (Token or credentials)
        scheme (str): Authorization scheme (Bearer, Basic, ApiKey, Token, JWT)

    Returns:
        Dict[str, str]: Dictionary chứa Authorization header (Dictionary containing Authorization header)

    Examples:
        >>> get_authorization_header('my-token')
        {'Authorization': 'Bearer my-token'}

        >>> get_authorization_header('api-key-123', scheme='ApiKey')
        {'Authorization': 'ApiKey api-key-123'}
    """
    # Normalize scheme
    scheme_normalized = scheme.lower()
    auth_prefix = AUTH_SCHEMES.get(scheme_normalized, scheme)

    return {"Authorization": f"{auth_prefix} {token}"}


def merge_headers(*header_dicts: Optional[Dict[str, str]]) -> Dict[str, str]:
    """
    Merge multiple header dictionaries with left-to-right priority.
    Headers from later dicts will override headers from earlier dicts.

    Args:
        *header_dicts: Dictionaries to merge

    Returns:
        Dict[str, str]: Merged headers dictionary

    Examples:
        >>> base = {'Content-Type': 'application/json'}
        >>> custom = {'X-Custom': 'value'}
        >>> merge_headers(base, custom)
        {'Content-Type': 'application/json', 'X-Custom': 'value'}

        >>> override = {'Content-Type': 'text/plain'}
        >>> merge_headers(base, custom, override)
        {'Content-Type': 'text/plain', 'X-Custom': 'value'}
    """
    result = {}
    for headers in header_dicts:
        if headers:
            result.update(headers)
    return result


def validate_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """
    Validate and clean headers dictionary.

    Args:
        headers (Dict[str, str]): Headers to validate

    Returns:
        Dict[str, str]: Validated headers

    Note:
        - Remove None or empty string values
        - Ensure all keys and values are strings
    """
    validated = {}
    for key, value in headers.items():
        if value is not None and value != "":
            validated[str(key)] = str(value)
    return validated


def get_headers(
    data_source: str = "SSI",
    random_agent: bool = False,
    browser: str = "chrome",
    platform: str = "windows",
    authorization: Optional[str] = None,
    auth_scheme: str = "Bearer",
    custom_headers: Optional[Dict[str, str]] = None,
    override_headers: Optional[Dict[str, str]] = None,
    include_defaults: bool = True,
) -> Dict[str, str]:
    """
    Generate request headers with optional referer/origin, a stable User-Agent,
    and support for Authorization and custom headers.

    Args:
        data_source (str): Predefined data source (e.g., 'SSI', 'VND', 'TCBS', 'XNO').
        random_agent (bool): Deprecated and ignored. User-Agent rotation was
            removed; headers are now stable across requests. Đã lỗi thời và bị bỏ
            qua. Cơ chế xoay vòng User-Agent đã được gỡ; header nay cố định.
        browser (str): Browser name to simulate if not random.
        platform (str): Platform name to simulate if not random.
        authorization (Optional[str]): Authorization token/key to include in headers.
        auth_scheme (str): Authorization scheme (Bearer, Basic, ApiKey, Token, JWT).
        custom_headers (Optional[Dict[str, str]]): Additional custom headers to merge.
        override_headers (Optional[Dict[str, str]]): Headers to override (highest priority).
        include_defaults (bool): Whether to include DEFAULT_HEADERS as base.

    Returns:
        Dict[str, str]: HTTP headers with realistic settings.

    Examples:
        >>> # Basic usage (backward compatible)
        >>> headers = get_headers(data_source='TCBS')

        >>> # With authorization
        >>> headers = get_headers(data_source='XNO', authorization='my-api-key')

        >>> # With custom headers
        >>> headers = get_headers(
        ...     data_source='TCBS',
        ...     custom_headers={'X-Request-ID': 'req-123'}
        ... )

        >>> # With override
        >>> headers = get_headers(
        ...     data_source='VCI',
        ...     override_headers={'Content-Type': 'application/x-www-form-urlencoded'}
        ... )

        >>> # Combined usage
        >>> headers = get_headers(
        ...     data_source='TCBS',
        ...     random_agent=True,
        ...     authorization='token-xyz',
        ...     auth_scheme='Bearer',
        ...     custom_headers={'X-Session': 'abc'},
        ...     override_headers={'Cache-Control': 'max-age=3600'}
        ... )
    """
    # Step 1: Start with default headers (if enabled)
    if include_defaults:
        headers = DEFAULT_HEADERS.copy()
    else:
        headers = {}

    # Step 2: Get source-specific configuration
    source_config = HEADERS_MAPPING_SOURCE.get(data_source.upper(), {})

    # Step 3: Add source-specific headers (if any)
    source_headers = source_config.get("headers", {})
    if source_headers:
        headers.update(source_headers)

    # Step 4: Determine and set User-Agent
    # `random_agent` no longer rotates the User-Agent. Rotating it across requests
    # served only to prevent a data source from recognising repeated calls as
    # coming from one client, which is not behaviour this library provides.
    if random_agent:
        warnings.warn(
            "Tham số 'random_agent' đã lỗi thời và không còn tác dụng. "
            "Cơ chế xoay vòng User-Agent đã được gỡ khỏi thư viện; "
            "hãy chỉ định 'browser' và 'platform' nếu cần một User-Agent cụ thể. "
            "The 'random_agent' parameter is deprecated and has no effect. "
            "User-Agent rotation has been removed; use 'browser' and 'platform' "
            "to select a specific User-Agent.",
            DeprecationWarning,
            stacklevel=2,
        )

    ua = USER_AGENTS.get(browser.lower(), {}).get(platform.lower())

    if not ua:
        # Fallback to first available platform under chrome or first browser available
        ua = USER_AGENTS.get("chrome", {}).get("windows")
        if not ua:
            # As a last resort, pick any user agent
            for b in USER_AGENTS.values():
                if isinstance(b, dict):
                    ua = next(iter(b.values()))
                    break

    if ua:
        headers["User-Agent"] = ua

    # Step 5: Add Referer and Origin from source config
    referer = source_config.get("Referer", "")
    origin = source_config.get("Origin", "")

    if referer:
        headers["Referer"] = referer
    if origin:
        headers["Origin"] = origin

    # Step 6: Add Authorization header (if provided)
    if authorization:
        auth_header = get_authorization_header(authorization, auth_scheme)
        headers.update(auth_header)

    # Step 7: Merge custom headers
    if custom_headers:
        headers.update(custom_headers)

    # Step 8: Apply override headers (highest priority)
    if override_headers:
        headers.update(override_headers)

    # Step 9: Source-specific dynamic transformations
    pass

    # Step 10: Validate and return
    return validate_headers(headers)
