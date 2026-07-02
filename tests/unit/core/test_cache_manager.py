"""Unit tests for CacheManager, backends, and make_cache_key."""

import time

import pytest


@pytest.mark.unit
@pytest.mark.core
class TestMakeCacheKey:
    def test_same_args_same_key(self):
        from vnstock.core.cache import make_cache_key

        k1 = make_cache_key(
            "KBS", "history", {"start": "2024-01-01", "end": "2024-12-31"}
        )
        k2 = make_cache_key(
            "KBS", "history", {"start": "2024-01-01", "end": "2024-12-31"}
        )
        assert k1 == k2

    def test_different_args_different_key(self):
        from vnstock.core.cache import make_cache_key

        k1 = make_cache_key("KBS", "history", {"start": "2024-01-01"})
        k2 = make_cache_key("KBS", "history", {"start": "2024-06-01"})
        assert k1 != k2

    def test_different_provider_different_key(self):
        from vnstock.core.cache import make_cache_key

        k1 = make_cache_key("KBS", "history", {})
        k2 = make_cache_key("VCI", "history", {})
        assert k1 != k2

    def test_kwargs_order_independent(self):
        from vnstock.core.cache import make_cache_key

        k1 = make_cache_key(
            "KBS", "history", {"start": "2024-01-01", "end": "2024-12-31"}
        )
        k2 = make_cache_key(
            "KBS", "history", {"end": "2024-12-31", "start": "2024-01-01"}
        )
        assert k1 == k2

    def test_returns_hex_string(self):
        from vnstock.core.cache import make_cache_key

        key = make_cache_key("KBS", "history", {})
        assert isinstance(key, str)
        assert len(key) == 64  # sha256 hex

    def test_domain_subdomain_scopes_key(self):
        """Same provider+method but different domains must produce different keys."""
        from vnstock.core.cache import make_cache_key

        k1 = make_cache_key(
            "KBS", "ohlcv", {"symbol": "VCB"}, domain="Market", subdomain="equity"
        )
        k2 = make_cache_key(
            "KBS", "ohlcv", {"symbol": "VCB"}, domain="Fundamental", subdomain="equity"
        )
        assert k1 != k2

    def test_same_domain_subdomain_same_key(self):
        """Identical calls with same domain/subdomain must be equal."""
        from vnstock.core.cache import make_cache_key

        k1 = make_cache_key(
            "KBS", "ohlcv", {"symbol": "VCB"}, domain="Market", subdomain="equity"
        )
        k2 = make_cache_key(
            "KBS", "ohlcv", {"symbol": "VCB"}, domain="Market", subdomain="equity"
        )
        assert k1 == k2


@pytest.mark.unit
@pytest.mark.core
class TestGetDefaultTtl:
    def test_market_domain_returns_3600(self):
        from vnstock.core.cache import get_default_ttl

        assert get_default_ttl("Market", "equity", "ohlcv") == 3600
        assert get_default_ttl("Market", "index", "ohlcv") == 3600

    def test_intraday_method_returns_3600(self):
        from vnstock.core.cache import get_default_ttl

        assert get_default_ttl("Market", "equity", "intraday") == 3600
        assert get_default_ttl("Market", "equity", "trades") == 3600

    def test_market_quote_returns_3600(self):
        from vnstock.core.cache import get_default_ttl

        assert get_default_ttl("Market", "equity", "quote") == 3600

    def test_reference_domain_returns_86400(self):
        from vnstock.core.cache import get_default_ttl

        assert get_default_ttl("Reference", "company", "info") == 86400
        assert get_default_ttl("Reference", "equity", "list") == 86400

    def test_fundamental_domain_returns_86400(self):
        from vnstock.core.cache import get_default_ttl

        assert get_default_ttl("Fundamental", "equity", "balance_sheet") == 86400
        assert get_default_ttl("Fundamental", "equity", "ratio") == 86400

    def test_fund_subdomain_returns_14400(self):
        from vnstock.core.cache import get_default_ttl

        assert get_default_ttl("Reference", "fund", "list") == 14400

    def test_retail_domain_returns_3600(self):
        from vnstock.core.cache import get_default_ttl

        assert get_default_ttl("Retail", "gold", "price") == 3600

    def test_unknown_domain_returns_minus_one(self):
        from vnstock.core.cache import get_default_ttl

        assert get_default_ttl("SomethingNew", "widget", "fetch") == -1


@pytest.mark.unit
@pytest.mark.core
class TestMemoryBackend:
    def setup_method(self):
        from vnstock.core.cache import MemoryBackend

        self.backend = MemoryBackend(max_size=3)

    def test_set_and_get(self):
        self.backend.set("k1", b"value1", ttl=60)
        assert self.backend.get("k1") == b"value1"

    def test_get_missing_returns_none(self):
        assert self.backend.get("nonexistent") is None

    def test_ttl_expiry(self):
        self.backend.set("k1", b"value", ttl=1)
        time.sleep(1.1)
        assert self.backend.get("k1") is None

    def test_lru_eviction_on_max_size(self):
        self.backend.set("k1", b"v1", ttl=60)
        self.backend.set("k2", b"v2", ttl=60)
        self.backend.set("k3", b"v3", ttl=60)
        # Adding k4 should evict the oldest (k1)
        self.backend.set("k4", b"v4", ttl=60)
        assert self.backend.get("k1") is None
        assert self.backend.get("k4") == b"v4"

    def test_clear_removes_all(self):
        self.backend.set("k1", b"v1", ttl=60)
        self.backend.set("k2", b"v2", ttl=60)
        self.backend.clear()
        assert self.backend.get("k1") is None
        assert self.backend.get("k2") is None

    def test_stats_returns_dict(self):
        self.backend.set("k1", b"v1", ttl=60)
        stats = self.backend.stats()
        assert stats["backend"] == "memory"
        assert stats["entries"] == 1


@pytest.mark.unit
@pytest.mark.core
class TestSQLiteBackend:
    def setup_method(self, tmp_path=None):
        import os
        import tempfile

        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test_cache.db")
        from vnstock.core.cache import SQLiteBackend

        self.backend = SQLiteBackend(path=self.db_path, max_size=100)

    def teardown_method(self):
        import shutil

        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_set_and_get(self):
        self.backend.set("k1", b"value1", ttl=60)
        assert self.backend.get("k1") == b"value1"

    def test_get_missing_returns_none(self):
        assert self.backend.get("missing") is None

    def test_ttl_expiry(self):
        self.backend.set("k1", b"value", ttl=1)
        time.sleep(1.1)
        assert self.backend.get("k1") is None

    def test_clear_removes_all(self):
        self.backend.set("k1", b"v1", ttl=60)
        self.backend.clear()
        assert self.backend.get("k1") is None

    def test_stats_returns_dict(self):
        self.backend.set("k1", b"v1", ttl=60)
        stats = self.backend.stats()
        assert stats["backend"] == "sqlite"
        assert stats["entries"] >= 1

    def test_survives_reinitialisation(self):
        """New SQLiteBackend instance reading same file sees cached data."""
        self.backend.set("persistent", b"data", ttl=3600)
        from vnstock.core.cache import SQLiteBackend

        backend2 = SQLiteBackend(path=self.db_path, max_size=100)
        assert backend2.get("persistent") == b"data"


@pytest.mark.unit
@pytest.mark.core
class TestCacheManager:
    def setup_method(self):
        from vnstock.core.cache import CacheManager
        from vnstock.core.settings import CacheConfig

        self.cfg_enabled = CacheConfig(
            enabled=True, ttl=300, max_size=100, backend="memory"
        )
        self.cfg_disabled = CacheConfig(
            enabled=False, ttl=300, max_size=100, backend="memory"
        )
        self.enabled = CacheManager(self.cfg_enabled)
        self.disabled = CacheManager(self.cfg_disabled)

    def test_get_set_roundtrip(self):
        import pandas as pd

        df = pd.DataFrame({"close": [100, 101]})
        self.enabled.set("key1", df, ttl=60)
        result = self.enabled.get("key1")
        assert result is not None
        assert list(result.columns) == ["close"]

    def test_disabled_manager_get_returns_none(self):
        import pandas as pd

        df = pd.DataFrame({"close": [100]})
        self.disabled.set("key1", df, ttl=60)
        assert self.disabled.get("key1") is None

    def test_clear(self):
        import pandas as pd

        df = pd.DataFrame({"close": [100]})
        self.enabled.set("k1", df, ttl=60)
        self.enabled.clear()
        assert self.enabled.get("k1") is None

    def test_stats(self):
        stats = self.enabled.stats()
        assert "backend" in stats
        assert "enabled" in stats
        assert stats["enabled"] is True
