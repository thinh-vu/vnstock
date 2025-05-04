# vnstock/vnstock/core/utils/user_agent.py

import random
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


HEADERS_MAPPING_SOURCE = {
    'SSI': {'Referer': 'https://iboard.ssi.com.vn', 'Origin': 'https://iboard.ssi.com.vn'},
    'VND': {'Referer': 'https://dchart.vndirect.com.vn', 'Origin': 'https://dchart.vndirect.com.vn'},
    'TCBS': {'Referer': 'https://tcinvest.tcbs.com.vn/', 'Origin': 'https://tcinvest.tcbs.com.vn/'},
    'VCI': {'Referer': 'https://trading.vietcap.com.vn/', 'Origin': 'https://trading.vietcap.com.vn/'},
    'MSN': {'Referer': 'https://www.msn.com/', 'Origin': 'https://www.msn.com/'},
    'FMARKET': {'Referer': 'https://fmarket.vn/', 'Origin': 'https://fmarket.vn/'},
    'SJC': {'Referer': 'https://sjc.com.vn/bieu-do-gia-vang', 'Origin': 'https://sjc.com.vn'},
}

def get_headers(
    data_source: str = 'SSI',
    random_agent: bool = True,
    browser: str = 'chrome',
    platform: str = 'windows'
) -> dict:
    """
    Generate browser-like headers with optional referer/origin and realistic User-Agent.

    Args:
        data_source (str): Predefined data source (e.g., 'SSI', 'VND').
        random_agent (bool): Whether to use a random browser/platform User-Agent.
        browser (str): Browser name to simulate if not random.
        platform (str): Platform name to simulate if not random.

    Returns:
        dict: HTTP headers with realistic settings.
    """
    ref_origin = HEADERS_MAPPING_SOURCE.get(data_source.upper(), {})
    referer = ref_origin.get("Referer", "")
    origin = ref_origin.get("Origin", "")

    # Determine browser/platform
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

    headers = DEFAULT_HEADERS.copy()
    headers["User-Agent"] = ua
    if referer:
        headers["Referer"] = referer
    if origin:
        headers["Origin"] = origin
    return headers