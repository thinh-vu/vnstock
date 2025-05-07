import pytest
import pandas as pd
from vnstock.explorer.vci.listing import Listing

# Shared minimal payload for the “stock‐list” methods
STOCK_PAYLOAD = [
    {"id": "1", "symbol": "AAA", "organ_name": "Test A", "type": "STOCK"},
    {"id": "2", "symbol": "BBB", "organ_name": "Test B", "type": "STOCK"},
]

# Payload for ICB classification
ICB_PAYLOAD = [
    {"icb_name": "Foo", "en_icb_name": "FooEN", "icb_code": 100, "level": 3}
]

@pytest.mark.parametrize("method, expected_cols, payload", [
    ("symbols_by_exchange",   ["symbol", "type", "organ_name"], STOCK_PAYLOAD),
    ("symbols_by_group",      ["symbol", "type", "organ_name"], STOCK_PAYLOAD),
    ("symbols_by_industries", ["symbol", "type", "organ_name"], STOCK_PAYLOAD),
    ("all_government_bonds",  ["symbol", "type", "organ_name"], STOCK_PAYLOAD),
    ("all_covered_warrant",   ["symbol", "type", "organ_name"], STOCK_PAYLOAD),
    ("all_bonds",             ["symbol", "type", "organ_name"], STOCK_PAYLOAD),
    ("industries_icb",        ["icb_name", "en_icb_name", "icb_code", "level"], ICB_PAYLOAD),
])
def test_vci_listing_methods_return_dataframe(method, expected_cols, payload, monkeypatch):
    """
    Phase 2 functional smoke tests for VCI Listing.
    Ensure each method returns a non-empty DataFrame with the expected columns.
    """
    # Stub out the internal send_request to return our synthetic payload
    monkeypatch.setattr(
        "vnstock.explorer.vci.listing.send_request",
        lambda *args, **kwargs: payload
    )

    lst = Listing(random_agent=False, show_log=False)
    fn  = getattr(lst, method)

    # Most methods accept show_log & to_df; industries_icb returns a DataFrame directly
    if method == "industries_icb":
        df = fn()
    else:
        df = fn(show_log=False, to_df=True)

    # 1) Must be a DataFrame
    assert isinstance(df, pd.DataFrame), f"{method} did not return a DataFrame"

    # 2) Non-empty
    assert not df.empty, f"{method} returned an empty DataFrame"

    # 3) If payload had an 'id', ensure it's dropped
    if "id" in payload[0]:
        assert "id" not in df.columns

    # 4) Exact columns match
    assert list(df.columns) == expected_cols, f"{method} columns {list(df.columns)} != expected {expected_cols}"

    # 5) First-row values line up with payload
    for col in expected_cols:
        assert df.iloc[0][col] == payload[0][col]
