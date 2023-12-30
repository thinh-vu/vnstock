import pytest
import pandas as pd
from vnstock.funds import *


def assert_dataframe_not_empty(result):
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0


# Retrieve non-empty dataframe with default parameters
def test_default_parameters():
    result = funds_listing()
    assert_dataframe_not_empty(result)

    result = fund_details()
    assert_dataframe_not_empty(result)

    result = fund_filter()
    assert_dataframe_not_empty(result)

    result = fund_top_holding()
    assert_dataframe_not_empty(result)

    result = fund_industry_holding()
    assert_dataframe_not_empty(result)

    result = fund_nav_report()
    assert_dataframe_not_empty(result)

    result = fund_asset_holding()
    assert_dataframe_not_empty(result)


# Retrieve non-empty dataframe with specified parameters
def test_parameters_specified():
    result = funds_listing(fund_type="BALANCED")
    assert_dataframe_not_empty(result)

    result = funds_listing(fund_type="BOND")
    assert_dataframe_not_empty(result)

    result = funds_listing(fund_type="STOCK")
    assert_dataframe_not_empty(result)

    result = fund_details(symbol="SSISCA", type="top_holding_list")
    assert_dataframe_not_empty(result)

    result = fund_details(symbol="SSISCA", type="industry_holding_list")
    assert_dataframe_not_empty(result)

    result = fund_details(symbol="SSISCA", type="nav_report")
    assert_dataframe_not_empty(result)

    result = fund_details(symbol="SSISCA", type="asset_holding_list")
    assert_dataframe_not_empty(result)

    result = fund_filter(symbol="SSISCA")
    assert_dataframe_not_empty(result)

    result = fund_top_holding(fundId=23)
    assert_dataframe_not_empty(result)

    result = fund_industry_holding(fundId=23)
    assert_dataframe_not_empty(result)

    result = fund_nav_report(fundId=23)
    assert_dataframe_not_empty(result)

    result = fund_asset_holding(fundId=23)
    assert_dataframe_not_empty(result)


# Assert error with unsupported param input
def test_funds_listing_invalid_input():
    # expected ouput is a non-empty dataframe
    result = funds_listing(fund_type="INVALID")
    assert_dataframe_not_empty(result)


def test_fund_details_invalid_symbol():
    with pytest.raises(ValueError):
        fund_details(symbol="invalid_symbol")


def test_fund_details_invalid_type():
    with pytest.raises(ValueError):
        fund_details(type="invalid_type")


def test_fund_filter_invalid_symbol():
    with pytest.raises(ValueError):
        fund_filter(symbol="invalid_symbol")


def test_fund_top_holding_invalid_fund_id():
    with pytest.raises(requests.exceptions.HTTPError):
        fund_top_holding(fundId=999)


def test_fund_industry_holding_invalid_fund_id():
    with pytest.raises(requests.exceptions.HTTPError):
        fund_industry_holding(fundId=999)


def test_fund_asset_holding_invalid_fund_id():
    with pytest.raises(requests.exceptions.HTTPError):
        fund_asset_holding(fundId=999)


def test_fund_nav_report_invalid_fund_id():
    with pytest.raises(ValueError):
        fund_nav_report(fundId=999)
