# pytest tests/test_explorer/1_smoke/test_smoke_msn.py --maxfail=1 -q

import pytest
import pandas as pd

from vnstock.explorer.msn.const   import _CURRENCY_ID_MAP, _CRYPTO_ID_MAP, _GLOBAL_INDICES
from vnstock.explorer.msn.helper  import get_asset_type
from vnstock.explorer.msn.listing import Listing
from vnstock.explorer.msn.models  import TickerModel
from vnstock.explorer.msn.quote   import Quote

# A simple DataFrame stub
EMPTY_DF = pd.DataFrame()

@pytest.fixture(autouse=True)
def patch_msn(monkeypatch):
    # Stub out msn_apikey wherever it's imported
    stub_key = lambda *a, **k: "DUMMY_KEY"
    monkeypatch.setattr("vnstock.explorer.msn.helper.msn_apikey", stub_key)
    monkeypatch.setattr("vnstock.explorer.msn.listing.msn_apikey", stub_key)
    monkeypatch.setattr("vnstock.explorer.msn.quote.msn_apikey", stub_key)

    # Stub Listing.search_symbol_id and Quote._input_validation paths
    monkeypatch.setattr(Listing, "search_symbol_id", lambda self, *a, **k: EMPTY_DF)
    # We leave Quote._input_validation intact (it doesn't call msn_apikey)
    yield

def test_listing_search_symbol_id_returns_dataframe():
    lst = Listing(api_version="20250101", random_agent=False)
    df = lst.search_symbol_id(query="ABC", locale=None, limit=5, to_df=True)
    assert isinstance(df, pd.DataFrame)
    assert df.empty

@pytest.mark.parametrize("symbol_id,expected", [
    (next(iter(_CURRENCY_ID_MAP.values())), "currency"),
    (next(iter(_CRYPTO_ID_MAP.values())),   "crypto"),
    (next(iter(_GLOBAL_INDICES.values())),  "index"),
    ("UNKNOWN_ID",                          "Unknown"),
])
def test_get_asset_type(symbol_id, expected):
    assert get_asset_type(symbol_id) == expected

def test_quote_input_validation():
    # Quote.__init__ will use our stubbed msn_apikey -> no KeyError
    q = Quote(symbol_id="abcd", api_version="20250101", random_agent=False)
    tm = q._input_validation(start="2025-01-01", end="2025-05-01", interval="1D")
    assert isinstance(tm, TickerModel)
    assert tm.symbol == "abcd"
    assert tm.start  == "2025-01-01"
    assert tm.end    == "2025-05-01"
