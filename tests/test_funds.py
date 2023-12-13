import pandas as pd
from vnstock.funds import funds_listing

def assert_valid_dataframe(result):
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

class TestFundsListing:
    # Retrieve list of available funds with default parameters
    def test_default_parameters(self):
        result = funds_listing()
        assert_valid_dataframe(result)
    
    # Retrieve list of available funds with all parameters specified
    def test_all_parameters_specified(self):
        result = funds_listing(lang='en', fund_type="STOCK", mode="full", decor=False)
        assert_valid_dataframe(result)
    
    # Retrieve list of available funds with unsupported language
    def test_unsupported_language(self):
        result = funds_listing(lang='fr')
        assert_valid_dataframe(result)
    
    # Retrieve list of available funds with unsupported fund type
    def test_unsupported_fund_type(self):
        result = funds_listing(fund_type="INVALID")
        assert_valid_dataframe(result)