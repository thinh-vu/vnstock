import pytest
import pandas as pd
from vnstock.funds import *

def assert_is_dataframe(result):
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

# Retrieve dataframe with default parameters
def test_default_parameters():
    result1 = funds_listing()
    result2 = fund_details()
    result3 = fund_filter()
    result4 = fund_top_holding()
    result5 = fund_industry_holding()
    result6 = fund_nav_report()
    result7 = fund_asset_holding()

    assert_is_dataframe(result1)
    assert_is_dataframe(result2)
    assert_is_dataframe(result3)
    assert_is_dataframe(result4)
    assert_is_dataframe(result5)
    assert_is_dataframe(result6)
    assert_is_dataframe(result7)

# Retrieve dataframe with all parameters specified
def test_all_parameters_specified():
    result = funds_listing(lang='en', fund_type="STOCK", mode="full", decor=False)
    assert_is_dataframe(result)

# Retrieve dataframe with unsupported param input
def test_unsupported_param_input():
    result = funds_listing(fund_type="INVALID")
    assert_is_dataframe(result)