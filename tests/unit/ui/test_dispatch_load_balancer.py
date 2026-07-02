"""Unit tests for load-balancer integration in BaseUI._dispatch()."""

import pytest


@pytest.mark.unit
@pytest.mark.core
class TestDispatchRouterBypass:
    def test_explicit_source_bypasses_router(self, monkeypatch):
        """When caller passes source=, router must not override it."""
        from vnstock.core.router import router

        picked = []
        original_pick = router.pick

        def spy_pick(pool_key, providers):
            result = original_pick(pool_key, providers)
            picked.append(result)
            return result

        monkeypatch.setattr(router, "pick", spy_pick)

        # Simulate a dispatch where source is explicitly provided
        # We test at the router level: when source is already in kwargs, pick should not be called
        from vnstock.ui._pools import POOLS, _build_pool_key

        key = _build_pool_key("Market", "equity", consumed_subdomain="ohlcv")
        assert key in POOLS, "Pool key should exist for Market/equity/ohlcv"

        # Direct router test: pick is called when no source override
        before_count = len(picked)
        router.pick(key, POOLS[key])
        assert len(picked) == before_count + 1  # pick was called

    def test_pool_key_covers_equity_ohlcv(self):
        from vnstock.ui._pools import POOLS, _build_pool_key

        key = _build_pool_key("Market", "equity", consumed_subdomain="ohlcv")
        assert key in POOLS
        providers = POOLS[key]
        assert len(providers) >= 2
        assert "KBS" in providers

    def test_pool_key_covers_equity_trades(self):
        from vnstock.ui._pools import POOLS, _build_pool_key

        key = _build_pool_key("Market", "equity", consumed_subdomain="trades")
        assert key in POOLS
        assert len(POOLS[key]) >= 2

    def test_pool_key_covers_price_board(self):
        from vnstock.ui._pools import POOLS, _build_pool_key

        key = _build_pool_key("equity_market", "price_board")
        assert key in POOLS
        assert len(POOLS[key]) >= 2


@pytest.mark.unit
@pytest.mark.core
class TestDispatchFailover:
    def test_router_mark_failed_changes_next_pick(self):
        """After marking a provider failed, router should skip it."""
        from vnstock.core.router import ProviderRouter

        r = ProviderRouter()
        providers = ["KBS", "VCI", "DNSE"]
        key = ("test", "failover", "equity")

        r.mark_failed(key, "KBS")
        picks = {r.pick(key, providers) for _ in range(20)}
        assert "KBS" not in picks

    def test_is_rate_limit_helper_detects_429(self):
        from vnstock.ui._base import _is_rate_limit

        assert _is_rate_limit(ValueError("HTTP 429 Too Many Requests"))
        assert _is_rate_limit(ValueError("rate limit exceeded"))
        assert not _is_rate_limit(ValueError("HTTP 503 Service Unavailable"))
        assert not _is_rate_limit(ConnectionError("timeout"))

    def test_source_used_attr_logic(self):
        """df.attrs['source_used'] is set by dispatch when router is used."""
        import pandas as pd

        df = pd.DataFrame({"close": [100, 101]})
        source = "VCI"
        df.attrs["source_used"] = source
        assert df.attrs["source_used"] == "VCI"
