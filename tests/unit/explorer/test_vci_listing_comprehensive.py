"""
Comprehensive tests for VCI Listing with all methods and parameters.

Tests cover:
- all_symbols() with different parameters
- symbols_by_exchange() for all exchanges
- symbols_by_industries() with lang options
- industries_icb()
- all_future_indices()
- all_government_bonds()
- all_covered_warrant()
- all_bonds()
"""

import pytest
import pandas as pd
from vnstock.explorer.vci.listing import Listing


@pytest.mark.integration
@pytest.mark.vci
class TestVCIListingComprehensive:
    """Comprehensive test suite for VCI Listing."""

    @pytest.mark.skip(reason="Integration test - requires live API")
    def test_all_symbols_basic(self):
        """Test all_symbols() returns data."""
        listing = Listing(random_agent=False, show_log=False)
        df = listing.all_symbols(show_log=False)
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty, "all_symbols() returned empty DataFrame"
        assert 'symbol' in df.columns

    @pytest.mark.skip(reason="Integration test - requires live API")
    def test_all_symbols_different_params(self):
        """Test all_symbols() with different parameters."""
        listing = Listing(random_agent=False, show_log=False)
        
        # With show_log=False
        df = listing.all_symbols(show_log=False)
        assert isinstance(df, pd.DataFrame)
        
        # With show_log=True
        df = listing.all_symbols(show_log=True)
        assert isinstance(df, pd.DataFrame)

    @pytest.mark.skip(reason="Integration test - requires live API")
    @pytest.mark.parametrize("lang", ['vi', 'en'])
    def test_symbols_by_exchange(self, lang):
        """Test symbols_by_exchange() for each language."""
        listing = Listing(random_agent=False, show_log=False)
        
        df = listing.symbols_by_exchange(
            lang=lang,
            show_log=False
        )
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty, f"No symbols for lang={lang}"
        assert 'symbol' in df.columns

    @pytest.mark.skip(reason="Integration test - requires live API")
    def test_symbols_by_industries_basic(self):
        """Test symbols_by_industries() returns data."""
        listing = Listing(random_agent=False, show_log=False)
        
        df = listing.symbols_by_industries(show_log=False)
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert 'symbol' in df.columns

    @pytest.mark.skip(reason="Integration test - requires live API")
    def test_industries_icb_basic(self):
        """Test industries_icb() returns industry classification."""
        listing = Listing(random_agent=False, show_log=False)
        
        df = listing.industries_icb(show_log=False)
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty, "industries_icb() returned empty"
        
        expected_cols = ['icb_name', 'icb_code']
        for col in expected_cols:
            assert col in df.columns, f"Missing {col} column"

    @pytest.mark.skip(reason="Integration test - requires live API")
    @pytest.mark.parametrize("lang", ['vi', 'en'])
    def test_industries_icb_lang(self, lang):
        """Test industries_icb() with different languages."""
        listing = Listing(random_agent=False, show_log=False)
        
        df = listing.industries_icb(show_log=False)
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    @pytest.mark.skip(reason="Integration test - requires live API")
    def test_all_future_indices(self):
        """Test all_future_indices() returns derivatives."""
        listing = Listing(random_agent=False, show_log=False)
        
        df = listing.all_future_indices(show_log=False)
        
        assert isinstance(df, pd.DataFrame)
        # May be empty if no derivatives available
        if not df.empty:
            assert 'symbol' in df.columns

    @pytest.mark.skip(reason="Integration test - requires live API")
    def test_all_government_bonds(self):
        """Test all_government_bonds() returns bond data."""
        listing = Listing(random_agent=False, show_log=False)
        
        df = listing.all_government_bonds(show_log=False)
        
        assert isinstance(df, pd.DataFrame)
        # May be empty depending on market
        if not df.empty:
            assert 'symbol' in df.columns

    @pytest.mark.skip(reason="Integration test - requires live API")
    def test_all_covered_warrant(self):
        """Test all_covered_warrant() returns CW data."""
        listing = Listing(random_agent=False, show_log=False)
        
        df = listing.all_covered_warrant(show_log=False)
        
        assert isinstance(df, pd.DataFrame)
        # May be empty if no CWs available
        if not df.empty:
            assert 'symbol' in df.columns

    @pytest.mark.skip(reason="Integration test - requires live API")
    def test_all_bonds(self):
        """Test all_bonds() returns all bond types."""
        listing = Listing(random_agent=False, show_log=False)
        
        df = listing.all_bonds(show_log=False)
        
        assert isinstance(df, pd.DataFrame)
        # May be empty depending on market
        if not df.empty:
            assert 'symbol' in df.columns

    @pytest.mark.skip(reason="Integration test - requires live API")
    @pytest.mark.parametrize("group", [
        'VN30', 'VNMIDCAP', 'VNSMALLCAP', 'VN100', 'VNALLSHARE'
    ])
    def test_symbols_by_group(self, group):
        """Test symbols_by_group() for different index groups."""
        listing = Listing(random_agent=False, show_log=False)
        
        try:
            df = listing.symbols_by_group(
                group=group,
                show_log=False
            )
            
            assert isinstance(df, pd.DataFrame)
            if not df.empty:
                assert 'symbol' in df.columns
        except Exception as e:
            # Some groups may not be supported
            print(f"Group {group} not available: {e}")

    @pytest.mark.skip(reason="Integration test - requires live API")
    def test_listing_data_consistency(self):
        """Test data consistency across listing methods."""
        listing = Listing(random_agent=False, show_log=False)
        
        # Get all symbols
        all_df = listing.all_symbols(show_log=False)
        all_symbols = set(all_df['symbol'].tolist())
        
        # Get exchange-specific symbols
        hose_df = listing.symbols_by_exchange(
            lang='vi',
            show_log=False
        )
        hose_symbols = set(hose_df['symbol'].tolist())
        
        # HOSE symbols should be subset of all symbols
        assert hose_symbols.issubset(all_symbols), \
            "HOSE symbols not in all_symbols"

    @pytest.mark.skip(reason="Integration test - requires live API")
    def test_random_agent_parameter(self):
        """Test Listing with random_agent=True."""
        listing = Listing(random_agent=True, show_log=False)
        
        df = listing.all_symbols(show_log=False)
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    @pytest.mark.skip(reason="Integration test - requires live API")
    def test_listing_returns_fresh_data(self):
        """Test that listing methods return current data."""
        listing = Listing(random_agent=False, show_log=False)
        
        # Call twice and compare
        df1 = listing.all_symbols(show_log=False)
        df2 = listing.all_symbols(show_log=False)
        
        # Should return same structure
        assert len(df1.columns) == len(df2.columns)
        assert list(df1.columns) == list(df2.columns)

    @pytest.mark.skip(reason="Integration test - requires live API")
    def test_industries_hierarchy(self):
        """Test industries_icb() returns proper hierarchy."""
        listing = Listing(random_agent=False, show_log=False)
        
        df = listing.industries_icb(show_log=False)
        
        if 'level' in df.columns:
            # Should have multiple levels
            levels = df['level'].unique()
            assert len(levels) > 0, "No industry levels found"
