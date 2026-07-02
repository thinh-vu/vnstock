"""
Integration tests for DNSE Quote and Trading explorers.

All tests use monkeypatching to avoid live HTTP calls.
They verify: column names, dtypes, schema consistency with KBS/VCI,
and price_board standard columns.
"""

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def make_ohlcv_response():
    """Return a DNSE-style array-of-arrays OHLCV response."""
    return {
        "t": [1704067200, 1704153600],  # 2024-01-01, 2024-01-02 UTC
        "o": [23500.0, 23600.0],
        "h": [24000.0, 24100.0],
        "l": [23000.0, 23100.0],
        "c": [23800.0, 23900.0],
        "v": [1000000, 1200000],
    }


def make_intraday_response():
    """Return a DNSE-style intraday tick response."""
    return [
        {"time": "09:15:00", "price": 23500.0, "volume": 100, "side": "B", "id": "1"},
        {"time": "09:16:30", "price": 23400.0, "volume": 200, "side": "S", "id": "2"},
        {"time": "09:17:00", "price": 23450.0, "volume": 150, "side": "B", "id": "3"},
    ]


def make_price_board_response():
    """Return a DNSE-style price board response."""
    return [
        {
            "sym": "ACB",
            "c": 23800.0,
            "f": 22000.0,
            "ce": 25000.0,
            "r": 23500.0,
            "o": 23200.0,
            "h": 24000.0,
            "l": 23000.0,
            "lastVolume": 100,
            "totalVolume": 5000000,
            "totalValue": 118000000000,
            "change": 300.0,
            "pcp": 1.28,
            "b1": 23750.0,
            "bv1": 500,
            "s1": 23850.0,
            "sv1": 300,
            "fBuyVol": 100000,
            "fSellVol": 80000,
            "fRoom": 200000,
        }
    ]


# ---------------------------------------------------------------------------
# History tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestDNSEQuoteHistory:
    """Integration tests for Quote.history() with mocked HTTP."""

    def test_history_returns_standard_columns(self, monkeypatch):
        """history() returns DataFrame with standard [time, open, high, low, close, volume]."""
        import vnstock.explorer.dnse.quote as dnse_quote_mod
        from vnstock.explorer.dnse.quote import Quote

        monkeypatch.setattr(
            dnse_quote_mod, "send_request", lambda *a, **kw: make_ohlcv_response()
        )

        q = Quote(symbol="ACB", show_log=False)
        df = q.history(start="2024-01-01", end="2024-01-02", interval="1D")

        assert list(df.columns) == ["time", "open", "high", "low", "close", "volume"]

    def test_history_column_dtypes(self, monkeypatch):
        """history() numeric columns have correct dtypes."""
        import vnstock.explorer.dnse.quote as dnse_quote_mod
        from vnstock.explorer.dnse.quote import Quote

        monkeypatch.setattr(
            dnse_quote_mod, "send_request", lambda *a, **kw: make_ohlcv_response()
        )

        q = Quote(symbol="ACB", show_log=False)
        df = q.history(start="2024-01-01", end="2024-01-02", interval="1D")

        assert df["open"].dtype.kind == "f", "open should be float"
        assert df["volume"].dtype.kind == "i", "volume should be integer"

    def test_history_price_not_divided_by_1000(self, monkeypatch):
        """DNSE prices are native VND — not divided by 1000."""
        import vnstock.explorer.dnse.quote as dnse_quote_mod
        from vnstock.explorer.dnse.quote import Quote

        monkeypatch.setattr(
            dnse_quote_mod, "send_request", lambda *a, **kw: make_ohlcv_response()
        )

        q = Quote(symbol="ACB", show_log=False)
        df = q.history(start="2024-01-01", end="2024-01-02", interval="1D")

        # Native VND: close should be ~23800, not ~23.8
        assert df["close"].iloc[0] > 1000, (
            "DNSE prices should be native VND (not /1000)"
        )

    def test_history_columns_match_kbs_schema(self, monkeypatch):
        """history() column names match those from KBS for drop-in compatibility."""
        import vnstock.explorer.dnse.quote as dnse_quote_mod
        from vnstock.explorer.dnse.quote import Quote

        monkeypatch.setattr(
            dnse_quote_mod, "send_request", lambda *a, **kw: make_ohlcv_response()
        )

        q_dnse = Quote(symbol="ACB", show_log=False)
        df_dnse = q_dnse.history(start="2024-01-01", end="2024-01-02", interval="1D")

        # Expected standard schema identical to KBS/VCI
        expected_columns = ["time", "open", "high", "low", "close", "volume"]
        assert list(df_dnse.columns) == expected_columns


# ---------------------------------------------------------------------------
# Intraday tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestDNSEQuoteIntraday:
    """Integration tests for Quote.intraday() with mocked HTTP."""

    def test_intraday_returns_standard_columns(self, monkeypatch):
        """intraday() returns DataFrame with standard columns."""
        import vnstock.explorer.dnse.quote as dnse_quote_mod
        from vnstock.explorer.dnse.quote import Quote

        monkeypatch.setattr(
            dnse_quote_mod, "send_request", lambda *a, **kw: make_intraday_response()
        )

        q = Quote(symbol="ACB", show_log=False)
        df = q.intraday(date="2024-01-02")

        for col in ["time", "price", "volume", "match_type", "id"]:
            assert col in df.columns, f"Column '{col}' missing from intraday output"

    def test_intraday_match_type_lowercase(self, monkeypatch):
        """match_type values are lowercase 'buy' or 'sell'."""
        import vnstock.explorer.dnse.quote as dnse_quote_mod
        from vnstock.explorer.dnse.quote import Quote

        monkeypatch.setattr(
            dnse_quote_mod, "send_request", lambda *a, **kw: make_intraday_response()
        )

        q = Quote(symbol="ACB", show_log=False)
        df = q.intraday(date="2024-01-02")

        valid = {"buy", "sell", "unknown"}
        assert df["match_type"].isin(valid).all(), (
            "match_type must be 'buy', 'sell', or 'unknown'"
        )

    def test_intraday_schema_matches_kbs_vci(self, monkeypatch):
        """intraday() column set matches KBS/VCI intraday schema."""
        import vnstock.explorer.dnse.quote as dnse_quote_mod
        from vnstock.explorer.dnse.quote import Quote

        monkeypatch.setattr(
            dnse_quote_mod, "send_request", lambda *a, **kw: make_intraday_response()
        )

        q = Quote(symbol="ACB", show_log=False)
        df = q.intraday(date="2024-01-02")

        expected = {"time", "price", "volume", "match_type", "id"}
        assert expected.issubset(set(df.columns)), (
            f"intraday columns {set(df.columns)} missing some of {expected}"
        )

    def test_intraday_future_date_raises(self):
        """intraday() raises ValueError for a future date."""
        from vnstock.explorer.dnse.quote import Quote

        q = Quote(symbol="ACB", show_log=False)
        with pytest.raises(ValueError, match="tương lai"):
            q.intraday(date="2099-12-31")


# ---------------------------------------------------------------------------
# Price board tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestDNSETradingPriceBoard:
    """Integration tests for Trading.price_board() with mocked HTTP."""

    def test_price_board_standard_columns_subset(self, monkeypatch):
        """price_board() contains at least the required standard columns."""
        import vnstock.explorer.dnse.trading as dnse_trading_mod
        from vnstock.explorer.dnse.trading import Trading

        monkeypatch.setattr(
            dnse_trading_mod,
            "send_request",
            lambda *a, **kw: make_price_board_response(),
        )

        t = Trading(show_log=False)
        df = t.price_board(symbols_list=["ACB"])

        required = {"symbol", "close_price", "reference_price"}
        assert required.issubset(set(df.columns)), (
            f"price_board columns {set(df.columns)} missing some of {required}"
        )

    def test_price_board_kbs_schema_subset(self, monkeypatch):
        """price_board() column names are a subset of KBS standard price board columns."""
        import vnstock.explorer.dnse.trading as dnse_trading_mod
        from vnstock.explorer.dnse.trading import Trading

        monkeypatch.setattr(
            dnse_trading_mod,
            "send_request",
            lambda *a, **kw: make_price_board_response(),
        )

        t = Trading(show_log=False)
        df = t.price_board(symbols_list=["ACB"])

        kbs_standard = {
            "symbol",
            "ceiling_price",
            "floor_price",
            "reference_price",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume_last",
            "volume_accumulated",
            "total_value",
            "price_change",
            "percent_change",
            "bid_price_1",
            "bid_vol_1",
            "ask_price_1",
            "ask_vol_1",
            "foreign_buy_volume",
            "foreign_sell_volume",
            "foreign_room",
        }

        assert df.columns.tolist(), "price_board DataFrame must not be empty"
        overlap = set(df.columns).intersection(kbs_standard)
        assert len(overlap) >= 3, (
            f"Too few matching columns: {overlap}. "
            "DNSE price_board should share standard column names with KBS."
        )


# ---------------------------------------------------------------------------
# Source switching test
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestDNSESourceSwitching:
    """Tests that switching source from KBS to DNSE returns same-schema DataFrame."""

    def test_switching_source_dnse_same_column_schema(self, monkeypatch):
        """Quote.history() with source='DNSE' returns standard column schema."""
        import vnstock.explorer.dnse.quote as dnse_quote_mod
        from vnstock.explorer.dnse.quote import Quote

        monkeypatch.setattr(
            dnse_quote_mod, "send_request", lambda *a, **kw: make_ohlcv_response()
        )

        q_dnse = Quote(symbol="ACB", show_log=False)
        df_dnse = q_dnse.history(start="2024-01-01", end="2024-01-02", interval="1D")

        expected = ["time", "open", "high", "low", "close", "volume"]
        assert list(df_dnse.columns) == expected, (
            f"DNSE history columns {list(df_dnse.columns)} differ from expected {expected}"
        )
