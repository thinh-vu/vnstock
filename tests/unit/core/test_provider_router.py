"""Unit tests for ProviderRouter (vnstock/core/router.py)."""

import threading

import pytest


@pytest.mark.unit
@pytest.mark.core
class TestProviderRouterRoundRobin:
    def setup_method(self):
        from vnstock.core.router import ProviderRouter

        self.router = ProviderRouter()

    def test_pick_returns_first_provider_initially(self):
        providers = ["KBS", "VCI", "DNSE"]
        result = self.router.pick(("Market", "equity", "ohlcv"), providers)
        assert result in providers

    def test_pick_rotates_round_robin(self):
        providers = ["KBS", "VCI", "DNSE"]
        key = ("Market", "equity", "ohlcv")
        results = [self.router.pick(key, providers) for _ in range(6)]
        # Each provider should appear at least once in 6 rounds of 3
        assert set(results) == {"KBS", "VCI", "DNSE"}

    def test_pick_cycles_deterministically(self):
        providers = ["A", "B", "C"]
        key = ("test", "cycle")
        picks = [self.router.pick(key, providers) for _ in range(9)]
        assert picks == ["A", "B", "C", "A", "B", "C", "A", "B", "C"]

    def test_pick_single_provider_always_returns_it(self):
        key = ("company", "info")
        for _ in range(3):
            assert self.router.pick(key, ["KBS"]) == "KBS"


@pytest.mark.unit
@pytest.mark.core
class TestProviderRouterCooldown:
    def setup_method(self):
        from vnstock.core.router import ProviderRouter

        self.router = ProviderRouter()

    def test_mark_failed_skips_provider_during_cooldown(self):
        providers = ["KBS", "VCI", "DNSE"]
        key = ("Market", "equity", "ohlcv")
        self.router.mark_failed(key, "KBS", is_rate_limit=False)
        # All picks in next ~60s should not return KBS
        picks = [self.router.pick(key, providers) for _ in range(10)]
        assert "KBS" not in picks

    def test_rate_limit_uses_longer_cooldown(self):
        providers = ["KBS", "VCI"]
        key = ("Market", "equity", "trades")
        self.router.mark_failed(key, "KBS", is_rate_limit=True)
        picks = [self.router.pick(key, providers) for _ in range(10)]
        assert all(p == "VCI" for p in picks)

    def test_all_in_cooldown_returns_a_provider(self):
        providers = ["KBS", "VCI"]
        key = ("Market", "equity", "quote")
        self.router.mark_failed(key, "KBS")
        self.router.mark_failed(key, "VCI")
        # Must still return something (best-effort)
        result = self.router.pick(key, providers)
        assert result in providers

    def test_reset_clears_state(self):
        providers = ["KBS", "VCI", "DNSE"]
        key = ("Market", "equity", "ohlcv")
        self.router.mark_failed(key, "KBS")
        self.router.reset()
        # After reset KBS should be pickable again
        picks = [self.router.pick(key, providers) for _ in range(9)]
        assert "KBS" in picks


@pytest.mark.unit
@pytest.mark.core
class TestProviderRouterThreadSafety:
    def test_concurrent_picks_do_not_crash(self):
        from vnstock.core.router import ProviderRouter

        router = ProviderRouter()
        providers = ["KBS", "VCI", "DNSE"]
        key = ("Market", "equity", "ohlcv")
        errors = []

        def worker():
            try:
                for _ in range(100):
                    router.pick(key, providers)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Thread errors: {errors}"
