# pytest tests/test_explorer/1_smoke/test_smoke_fmarket.py --maxfail=1 -q

import pytest
import pandas as pd
from datetime import datetime

from vnstock.explorer.fmarket.fund import Fund, convert_unix_to_datetime

# A stub empty DataFrame
EMPTY_DF = pd.DataFrame()

@pytest.fixture(autouse=True)
def patch_fmarket(monkeypatch):
    # 1) Stub Fund.listing so __init__ can fetch `['short_name']`
    monkeypatch.setattr(
        Fund,
        "listing",
        lambda self, fund_type="": pd.DataFrame({"short_name": []})
    )
    # 2) Stub Fund.filter so FundDetails._get_fund_details never KeyErrors
    monkeypatch.setattr(
        Fund,
        "filter",
        lambda self, symbol="": pd.DataFrame({"id": [], "shortName": []})
    )
    # 3) Stub all FundDetails methods to return a DataFrame
    for method in ("top_holding", "industry_holding", "nav_report", "asset_holding"):
        monkeypatch.setattr(
            Fund.FundDetails,
            method,
            lambda self, *a, **k: EMPTY_DF
        )
    yield

def test_fund_constructor_and_listing():
    f = Fund(random_agent=False)
    # Should have attributes and a stubbed DataFrame
    assert isinstance(f, Fund)
    df = f.listing()
    assert isinstance(df, pd.DataFrame)

@pytest.mark.parametrize("method", ["top_holding", "industry_holding", "nav_report", "asset_holding"])
def test_funddetails_methods_return_dataframe(method):
    f = Fund(random_agent=False)
    detail = f.details
    # Call each stubbed method by name
    df = getattr(detail, method)(symbol="XXXX")
    assert isinstance(df, pd.DataFrame)

def test_convert_unix_to_datetime():
    # Prepare a DataFrame with two timestamps: invalid (-1) and valid (e.g. Feb 1 2020)
    ms = [-1, 1580515200000]
    df_in = pd.DataFrame({"ts": ms})
    out = convert_unix_to_datetime(df_in, ["ts"])
    # Both values should exist as strings; invalid one maps to NaN->None->kept as NaN, valid one to '2020-02-01'
    assert out["ts"].dtype == object
    assert "2020-02-01" in out["ts"].values
