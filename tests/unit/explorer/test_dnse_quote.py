"""
Unit tests for DNSE Quote explorer.

These tests assert the expected API contract for the DNSE data provider
before the implementation exists (TDD: start red, turn green in task group 4).
"""

import pytest


@pytest.mark.unit
@pytest.mark.explorer
class TestDNSEQuoteInstantiation:
    """Basic instantiation tests for DNSE Quote."""

    def test_quote_instantiation(self):
        """DNSE Quote can be instantiated after module import."""
        from vnstock.explorer.dnse.quote import Quote

        q = Quote(symbol="VCB", show_log=False)
        assert q is not None
        assert q.symbol == "VCB"
        assert q.data_source == "DNSE"

    def test_quote_symbol_uppercased(self):
        """Symbol is normalised to uppercase on init."""
        from vnstock.explorer.dnse.quote import Quote

        q = Quote(symbol="vcb", show_log=False)
        assert q.symbol == "VCB"

    def test_invalid_interval_raises_value_error(self):
        """history() with an invalid interval raises ValueError."""
        from vnstock.explorer.dnse.quote import Quote

        q = Quote(symbol="VCB", show_log=False)
        with pytest.raises(ValueError):
            q.history(start="2024-01-01", end="2024-01-31", interval="INVALID")

    def test_provider_registered_after_import(self):
        """ProviderRegistry resolves 'quote'/'dnse' after module import."""
        import vnstock.explorer.dnse.quote  # noqa: F401 — triggers self-registration
        from vnstock.core.registry import ProviderRegistry

        cls = ProviderRegistry.get("quote", "dnse")
        assert cls is not None
        assert cls.__name__ == "Quote"

    def test_source_dnse_accepted_by_api_quote_adapter(self):
        """BaseAdapter-based Quote accepts source='DNSE' without raising."""
        from vnstock.api.quote import Quote as APIQuote

        q = APIQuote(source="DNSE", symbol="VCB", show_log=False)
        assert q.source.lower() == "dnse"
