"""
Unit tests for the retry policy's handling of HTTP status and environment errors.

No network: requests.get is patched and the backoff is reduced to zero.
"""

from unittest import mock

import pytest
import requests
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_none

from vnstock.core.exceptions import HTTPStatusError, UnsupportedEnvironmentError
from vnstock.core.utils.client import send_request
from vnstock.core.utils.retry import should_retry


def _response(status: int) -> requests.Response:
    resp = requests.Response()
    resp.status_code = status
    resp.reason = "test"
    resp._content = b"{}"
    resp.headers["Content-Type"] = "application/json"
    return resp


def _fast_retry(func):
    """Same predicate as api_retry, without the real backoff."""
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_none(),
        retry=retry_if_exception(should_retry),
        reraise=True,
    )(func)


@pytest.mark.unit
class TestHTTPStatusRetry:
    @pytest.mark.parametrize("status", [400, 401, 404, 422])
    def test_permanent_4xx_is_not_retried(self, status):
        calls = mock.Mock(return_value=_response(status))

        @_fast_retry
        def fetch():
            return send_request("https://api.example.com/x", headers={})

        with mock.patch("requests.get", calls):
            with pytest.raises(HTTPStatusError) as info:
                fetch()
        assert info.value.status_code == status
        assert calls.call_count == 1

    @pytest.mark.parametrize("status", [408, 500, 502, 503])
    def test_transient_status_is_retried(self, status):
        calls = mock.Mock(return_value=_response(status))

        @_fast_retry
        def fetch():
            return send_request("https://api.example.com/x", headers={})

        with mock.patch("requests.get", calls):
            with pytest.raises(HTTPStatusError):
                fetch()
        assert calls.call_count == 3

    def test_still_caught_as_connection_error(self):
        with mock.patch("requests.get", return_value=_response(404)):
            with pytest.raises(ConnectionError):
                send_request("https://api.example.com/x", headers={})


@pytest.mark.unit
class TestUnsupportedEnvironment:
    def test_is_never_retried(self):
        assert not should_retry(UnsupportedEnvironmentError("colab"))

    def test_still_caught_as_environment_error(self):
        with mock.patch("vnstock.core.utils.env.is_colab", return_value=True):
            with pytest.raises(EnvironmentError):
                send_request("https://trading.vietcap.com.vn/x", headers={})
