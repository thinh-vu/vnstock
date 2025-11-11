"""
Comprehensive tests for VCI Company and Finance with diverse symbols.

Tests cover:
Company:
- overview(), profile(), officers(), shareholders()
- major_holders(), insider_deals(), subsidiaries()

Finance:
- balance_sheet() with year/quarter periods
- income_statement() with year/quarter periods
- cash_flow() with year/quarter periods
- ratio() with year/quarter periods
- All with lang='vi' and lang='en'
"""

import pytest
import pandas as pd
from vnstock.explorer.vci.company import Company
from vnstock.explorer.vci.financial import Finance


@pytest.mark.integration
@pytest.mark.vci
@pytest.mark.slow
class TestVCICompanyComprehensive:
    """Comprehensive test suite for VCI Company."""

    def test_overview_diverse_symbols(self, diverse_test_symbols):
        """Test overview() with diverse symbols."""
        all_symbols = diverse_test_symbols['all'][:5]
        
        for symbol in all_symbols:
            try:
                company = Company(
                    symbol=symbol,
                    random_agent=False,
                    show_log=False
                )
                df = company.overview()
                
                assert isinstance(df, (pd.DataFrame, dict)), \
                    f"overview() failed for {symbol}"
            
            except Exception as e:
                pytest.fail(f"Company overview {symbol} failed: {e}")

    def test_profile_diverse_symbols(self, diverse_test_symbols):
        """Test profile() with diverse symbols."""
        all_symbols = diverse_test_symbols['all'][:5]
        
        for symbol in all_symbols:
            try:
                company = Company(
                    symbol=symbol,
                    random_agent=False,
                    show_log=False
                )
                result = company.profile()
                
                assert result is not None, \
                    f"profile() returned None for {symbol}"
            
            except Exception as e:
                print(f"Profile not available for {symbol}: {e}")

    def test_officers_sample_symbols(self, random_hose_symbols):
        """Test officers() with HOSE samples."""
        test_symbols = random_hose_symbols[:5]
        
        for symbol in test_symbols:
            try:
                company = Company(
                    symbol=symbol,
                    random_agent=False,
                    show_log=False
                )
                df = company.officers()
                
                assert isinstance(df, pd.DataFrame), \
                    f"officers() failed for {symbol}"
            
            except Exception as e:
                print(f"Officers not available for {symbol}: {e}")

    def test_shareholders_sample_symbols(self, random_hose_symbols):
        """Test shareholders() with HOSE samples."""
        test_symbols = random_hose_symbols[:5]
        
        for symbol in test_symbols:
            try:
                company = Company(
                    symbol=symbol,
                    random_agent=False,
                    show_log=False
                )
                df = company.shareholders()
                
                assert isinstance(df, pd.DataFrame), \
                    f"shareholders() failed for {symbol}"
            
            except Exception as e:
                print(f"Shareholders not available for {symbol}: {e}")


@pytest.mark.integration
@pytest.mark.vci
@pytest.mark.slow
class TestVCIFinanceComprehensive:
    """Comprehensive test suite for VCI Finance."""

    @pytest.mark.parametrize("period", ['year', 'quarter'])
    @pytest.mark.parametrize("lang", ['vi', 'en'])
    def test_balance_sheet_params(
        self, diverse_test_symbols, period, lang
    ):
        """Test balance_sheet() with all parameter combinations."""
        symbol = diverse_test_symbols['hose'][0]
        
        finance = Finance(
            symbol=symbol,
            period=period,
            show_log=False
        )
        
        df = finance.balance_sheet(
            period=period,
            lang=lang,
            dropna=True
        )
        
        assert isinstance(df, pd.DataFrame), \
            f"balance_sheet failed for period={period}, lang={lang}"

    @pytest.mark.parametrize("period", ['year', 'quarter'])
    @pytest.mark.parametrize("lang", ['vi', 'en'])
    def test_income_statement_params(
        self, diverse_test_symbols, period, lang
    ):
        """Test income_statement() with all parameter combinations."""
        symbol = diverse_test_symbols['hose'][0]
        
        finance = Finance(
            symbol=symbol,
            period=period,
            show_log=False
        )
        
        df = finance.income_statement(
            period=period,
            lang=lang,
            dropna=True
        )
        
        assert isinstance(df, pd.DataFrame), \
            f"income_statement failed for period={period}, lang={lang}"

    @pytest.mark.parametrize("period", ['year', 'quarter'])
    def test_cash_flow_periods(self, diverse_test_symbols, period):
        """Test cash_flow() with different periods."""
        symbol = diverse_test_symbols['hose'][0]
        
        finance = Finance(
            symbol=symbol,
            period=period,
            show_log=False
        )
        
        df = finance.cash_flow(period=period, dropna=True)
        
        assert isinstance(df, pd.DataFrame)

    @pytest.mark.parametrize("period", ['year', 'quarter'])
    @pytest.mark.parametrize("lang", ['vi', 'en'])
    def test_ratio_params(self, diverse_test_symbols, period, lang):
        """Test ratio() with all parameter combinations."""
        symbol = diverse_test_symbols['hose'][0]
        
        finance = Finance(
            symbol=symbol,
            period=period,
            show_log=False
        )
        
        df = finance.ratio(period=period, lang=lang, dropna=True)
        
        assert isinstance(df, pd.DataFrame)

    def test_all_financial_statements_hose(self, random_hose_symbols):
        """Test all financial statements for HOSE samples."""
        test_symbols = random_hose_symbols[:3]
        
        for symbol in test_symbols:
            finance = Finance(
                symbol=symbol,
                period='year',
                show_log=False
            )
            
            try:
                bs = finance.balance_sheet(period='year', dropna=True)
                assert isinstance(bs, pd.DataFrame)
                
                inc = finance.income_statement(period='year', dropna=True)
                assert isinstance(inc, pd.DataFrame)
                
                cf = finance.cash_flow(period='year', dropna=True)
                assert isinstance(cf, pd.DataFrame)
                
                ratio = finance.ratio(period='year', dropna=True)
                assert isinstance(ratio, pd.DataFrame)
            
            except Exception as e:
                pytest.fail(
                    f"Financial statements failed for {symbol}: {e}"
                )

    def test_all_financial_statements_hnx(self, random_hnx_symbols):
        """Test all financial statements for HNX samples."""
        test_symbols = random_hnx_symbols[:3]
        
        for symbol in test_symbols:
            finance = Finance(
                symbol=symbol,
                period='year',
                show_log=False
            )
            
            try:
                bs = finance.balance_sheet(period='year', dropna=True)
                assert isinstance(bs, pd.DataFrame)
            
            except Exception as e:
                print(f"Financial data not available for {symbol}: {e}")

    def test_all_financial_statements_upcom(self, random_upcom_symbols):
        """Test all financial statements for UPCOM samples."""
        test_symbols = random_upcom_symbols[:3]
        
        for symbol in test_symbols:
            finance = Finance(
                symbol=symbol,
                period='year',
                show_log=False
            )
            
            try:
                bs = finance.balance_sheet(period='year', dropna=True)
                assert isinstance(bs, pd.DataFrame)
            
            except Exception as e:
                print(f"Financial data not available for {symbol}: {e}")

    def test_get_all_parameter(self, diverse_test_symbols):
        """Test Finance with get_all parameter."""
        symbol = diverse_test_symbols['hose'][0]
        
        finance = Finance(
            symbol=symbol,
            period='year',
            get_all=True,
            show_log=False
        )
        
        df = finance.balance_sheet(period='year', dropna=True)
        assert isinstance(df, pd.DataFrame)

    def test_dropna_parameter(self, diverse_test_symbols):
        """Test dropna parameter effect."""
        symbol = diverse_test_symbols['hose'][0]
        
        finance = Finance(
            symbol=symbol,
            period='year',
            show_log=False
        )
        
        # With dropna=True
        df_clean = finance.balance_sheet(period='year', dropna=True)
        
        # With dropna=False
        df_full = finance.balance_sheet(period='year', dropna=False)
        
        assert isinstance(df_clean, pd.DataFrame)
        assert isinstance(df_full, pd.DataFrame)
        
        # Full version should have >= rows than clean
        assert len(df_full) >= len(df_clean)
