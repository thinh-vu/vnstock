import pytest
from vnstock.explorer.vci.quote import Quote
from vnstock.core.utils.browser_profiles import USER_AGENTS
from vnstock.core.utils.user_agent import HEADERS_MAPPING_SOURCE


def test_quote_with_default_headers():
    q = Quote("VCB", random_agent=False)
    headers = q.headers

    assert headers["User-Agent"] == USER_AGENTS["chrome"]["windows"]
    assert headers["Referer"] == HEADERS_MAPPING_SOURCE["VCI"]["Referer"]
    assert headers["Origin"] == HEADERS_MAPPING_SOURCE["VCI"]["Origin"]
    assert "Accept" in headers


def test_quote_with_random_agent():
    q1 = Quote("VCB", random_agent=True)
    q2 = Quote("VCB", random_agent=True)
    assert "User-Agent" in q1.headers
    assert "User-Agent" in q2.headers
    assert q1.headers["User-Agent"] != ""  # At least valid
    assert q2.headers["User-Agent"] != ""

# How to run
# python3.10 -m pytest tests/core/utils/test_quote_headers.py -v
