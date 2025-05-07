# tests/test_user_agent.py

import pytest
from vnstock.core.utils.user_agent import get_headers, HEADERS_MAPPING_SOURCE
from vnstock.core.utils.browser_profiles import USER_AGENTS

def test_default_headers_structure():
    headers = get_headers("VND", random_agent=False, browser="chrome", platform="windows")
    assert isinstance(headers, dict)
    assert "User-Agent" in headers
    assert "Accept" in headers
    assert "Referer" in headers
    assert headers["Referer"] == HEADERS_MAPPING_SOURCE["VND"]["Referer"]
    assert headers["Origin"] == HEADERS_MAPPING_SOURCE["VND"]["Origin"]

def test_random_headers_generation():
    # Run multiple times to ensure randomness is handled without error
    for _ in range(5):
        headers = get_headers("SSI", random_agent=True)
        assert "User-Agent" in headers
        assert headers["Referer"] == HEADERS_MAPPING_SOURCE["SSI"]["Referer"]

def test_explicit_browser_platform_combo():
    ua_pairs = [
        ("safari", "macos"),
        ("safari", "ios"),
        ("chrome", "windows"),
        ("chrome", "android"),
        ("firefox", "windows"),
        ("firefox", "android"),
    ]
    for browser, platform in ua_pairs:
        headers = get_headers("VCI", random_agent=False, browser=browser, platform=platform)
        assert "User-Agent" in headers
        expected = USER_AGENTS.get(browser, {}).get(platform)
        if expected:
            assert headers["User-Agent"] == expected

def test_invalid_browser_platform_fallback():
    headers = get_headers("TCBS", random_agent=False, browser="invalid", platform="none")
    # Fallback to chrome/windows
    assert headers["User-Agent"] == USER_AGENTS["chrome"]["windows"]

def test_data_source_not_found():
    headers = get_headers("UNKNOWN_SOURCE", random_agent=False)
    assert "User-Agent" in headers
    assert "Referer" not in headers
    assert "Origin" not in headers


# python3.10 -m pytest tests/core/utils/test_user_agent.py -v