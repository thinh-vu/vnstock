"""Tests for async HTTP client diagnostics."""

import asyncio

import httpx

from vnstock.core.utils.async_client import (
    async_send_request,
    get_async_request_stats,
    reset_async_request_stats,
)


class DummyResponse:
    def __init__(self, status_code: int, payload=None):
        self.status_code = status_code
        self._payload = payload or {"ok": True}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://example.com")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=request,
                response=response,
            )


class SequenceClient:
    def __init__(self, responses):
        self._responses = list(responses)

    async def request(self, method, url, **kwargs):
        result = self._responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def test_async_send_request_collects_success_stats(monkeypatch):
    reset_async_request_stats()

    async def fake_get_client(proxy_url=None):
        return SequenceClient([DummyResponse(200, {"value": 1})])

    monkeypatch.setattr(
        "vnstock.core.utils.async_client.async_client_mgr.get_client",
        fake_get_client,
    )

    result = asyncio.run(
        async_send_request(
            url="https://example.com",
            headers={"accept": "application/json"},
            proxy_list=["http://127.0.0.1:8080"],
        )
    )

    stats = get_async_request_stats()
    assert result == {"value": 1}
    assert stats["total_requests"] == 1
    assert stats["successful_requests"] == 1
    assert stats["failed_requests"] == 0
    assert stats["total_attempts"] == 1
    assert stats["retry_attempts"] == 0
    assert stats["proxied_requests"] == 1
    assert stats["status_counts"][200] == 1


def test_async_send_request_collects_retry_stats(monkeypatch):
    reset_async_request_stats()

    async def fake_get_client(proxy_url=None):
        return SequenceClient([
            DummyResponse(429),
            DummyResponse(200, {"value": 2}),
        ])

    monkeypatch.setattr(
        "vnstock.core.utils.async_client.async_client_mgr.get_client",
        fake_get_client,
    )

    result = asyncio.run(
        async_send_request(
            url="https://example.com",
            headers={"accept": "application/json"},
            retry_backoff_seconds=0,
        )
    )

    stats = get_async_request_stats()
    assert result == {"value": 2}
    assert stats["successful_requests"] == 1
    assert stats["failed_requests"] == 0
    assert stats["total_attempts"] == 2
    assert stats["retry_attempts"] == 1
    assert stats["throttled_responses"] == 1
    assert stats["status_counts"][429] == 1
    assert stats["status_counts"][200] == 1


def test_async_send_request_collects_timeout_stats(monkeypatch):
    reset_async_request_stats()

    async def fake_get_client(proxy_url=None):
        return SequenceClient([
            httpx.ReadTimeout("timed out"),
        ])

    monkeypatch.setattr(
        "vnstock.core.utils.async_client.async_client_mgr.get_client",
        fake_get_client,
    )

    try:
        asyncio.run(
            async_send_request(
                url="https://example.com",
                headers={"accept": "application/json"},
                max_retries=0,
            )
        )
    except ConnectionError:
        pass
    else:
        raise AssertionError("Expected ConnectionError")

    stats = get_async_request_stats()
    assert stats["successful_requests"] == 0
    assert stats["failed_requests"] == 1
    assert stats["timeout_errors"] == 1
    assert stats["total_attempts"] == 1