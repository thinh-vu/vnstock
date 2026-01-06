# vnstock/vnstock/core/utils/user_agent.py

import random
from typing import Optional, Dict
from vnstock.core.utils.browser_profiles import USER_AGENTS

DEFAULT_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'DNT': '1',
    'Pragma': 'no-cache',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-mobile': '?0',
}


BROWSER_PROFILES = {
    "chrome": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    },
    "safari": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/605.1.15 Version/16.3 Safari/605.1.15",
    },
    "coccoc": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0 CocCocBrowser/123.0",
    },
    "firefox": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    },
    "brave": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Brave/120.0.0.0 Safari/537.36",
    },
    "vivaldi": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Vivaldi/6.2.3105.58 Safari/537.36",
    },
}


# Enhanced HEADERS_MAPPING_SOURCE with support for source-specific headers
HEADERS_MAPPING_SOURCE = {
    'SSI': {
        'Referer': 'https://iboard.ssi.com.vn',
        'Origin': 'https://iboard.ssi.com.vn'
    },
    'VND': {
        'Referer': 'https://dchart.vndirect.com.vn',
        'Origin': 'https://dchart.vndirect.com.vn'
    },
    'TCBS': {
        'Referer': 'https://tcinvest.tcbs.com.vn/',
        'Origin': 'https://tcinvest.tcbs.com.vn/'
    },
    'VCI': {
        'Referer': 'https://trading.vietcap.com.vn/',
        'Origin': 'https://trading.vietcap.com.vn/'
    },
    'MSN': {
        'Referer': 'https://www.msn.com/',
        'Origin': 'https://www.msn.com/'
    },
    'FMARKET': {
        'Referer': 'https://fmarket.vn/',
        'Origin': 'https://fmarket.vn/'
    },
    'SJC': {
        'Referer': 'https://sjc.com.vn/bieu-do-gia-vang',
        'Origin': 'https://sjc.com.vn'
    }
}


# Supported authorization schemes
AUTH_SCHEMES = {
    'bearer': 'Bearer',
    'basic': 'Basic',
    'apikey': 'ApiKey',
    'token': 'Token',
    'jwt': 'Bearer',
}


def get_authorization_header(
    token: str,
    scheme: str = 'Bearer'
) -> Dict[str, str]:
    """
    Tạo Authorization header theo scheme cụ thể.

    Args:
        token (str): Token hoặc credentials
        scheme (str): Authorization scheme (Bearer, Basic, ApiKey, Token, JWT)

    Returns:
        Dict[str, str]: Dictionary chứa Authorization header

    Examples:
        >>> get_authorization_header('my-token')
        {'Authorization': 'Bearer my-token'}

        >>> get_authorization_header('api-key-123', scheme='ApiKey')
        {'Authorization': 'ApiKey api-key-123'}
    """
    # Normalize scheme
    scheme_normalized = scheme.lower()
    auth_prefix = AUTH_SCHEMES.get(scheme_normalized, scheme)

    return {'Authorization': f'{auth_prefix} {token}'}


def merge_headers(*header_dicts: Optional[Dict[str, str]]) -> Dict[str, str]:
    """
    Merge nhiều dictionaries của headers với thứ tự ưu tiên từ trái sang phải.
    Headers ở các dict sau sẽ override headers ở các dict trước.

    Args:
        *header_dicts: Các dictionaries cần merge

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
    Validate và clean headers dictionary.

    Args:
        headers (Dict[str, str]): Headers cần validate

    Returns:
        Dict[str, str]: Validated headers

    Note:
        - Loại bỏ các giá trị None hoặc empty string
        - Đảm bảo tất cả keys và values là strings
    """
    validated = {}
    for key, value in headers.items():
        if value is not None and value != '':
            validated[str(key)] = str(value)
    return validated


def get_headers(
    data_source: str = 'SSI',
    random_agent: bool = True,
    browser: str = 'chrome',
    platform: str = 'windows',
    authorization: Optional[str] = None,
    auth_scheme: str = 'Bearer',
    custom_headers: Optional[Dict[str, str]] = None,
    override_headers: Optional[Dict[str, str]] = None,
    include_defaults: bool = True
) -> Dict[str, str]:
    """
    Generate browser-like headers with optional referer/origin, realistic User-Agent,
    and support for Authorization and custom headers.

    Args:
        data_source (str): Predefined data source (e.g., 'SSI', 'VND', 'TCBS', 'XNO').
        random_agent (bool): Whether to use a random browser/platform User-Agent.
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
    source_headers = source_config.get('headers', {})
    if source_headers:
        headers.update(source_headers)

    # Step 4: Determine and set User-Agent
    if random_agent:
        browser = random.choice(list(USER_AGENTS.keys()))
        platform = random.choice(list(USER_AGENTS[browser].keys()))

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

    # Step 9: Validate and return
    return validate_headers(headers)