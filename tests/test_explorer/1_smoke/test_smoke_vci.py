# pytest tests/test_explorer/1_smoke/test_smoke_vci.py --maxfail=1 -q

import pytest
import pandas as pd

from vnstock.explorer.vci.quote import Quote
from vnstock.explorer.vci.company import Company
from vnstock.explorer.vci.financial import Finance
from vnstock.explorer.vci.listing import Listing
from vnstock.explorer.vci.trading import Trading
from vnstock.explorer.vci.models import TickerModel

# Dummy HTTP client response for Trading.price_board
class DummyPostResp:
    status_code = 200
    def json(self):
        return {}

@pytest.fixture(autouse=True)
def patch_vci(monkeypatch):
    # 1) Patch Company._fetch_data to include a valid icbName4
    monkeypatch.setattr(
        "vnstock.explorer.vci.company.Company._fetch_data",
        lambda self, *a, **k: {"CompanyListingInfo": {"icbName4": "Bán lẻ phức hợp"}}
    )
    # 2) Patch client.send_request (used by Listing & Finance) to return {"data": {}}
    monkeypatch.setattr(
        "vnstock.core.utils.client.send_request",
        lambda *a, **k: {"data": {}}
    )
    # 3) Patch HTTP POST for Trading.price_board
    monkeypatch.setattr("requests.post", lambda *a, **k: DummyPostResp())
    yield

def test_company_constructor():
    c = Company(symbol="AAA", random_agent=False, to_df=True, show_log=False)
    assert isinstance(c, Company)

def test_finance_constructor():
    f = Finance(symbol="AAA", period="quarter", get_all=True, show_log=False)
    assert isinstance(f, Finance)

def test_ticker_model_fields():
    tm = TickerModel(symbol="AAA", start="2025-01-01", end=None, interval="1D")
    assert tm.symbol == "AAA"
    assert tm.start == "2025-01-01"

def test_listing_all_symbols_returns_df():
    lst = Listing(random_agent=False, show_log=False)
    df = lst.all_symbols(show_log=False, to_df=True)
    assert isinstance(df, pd.DataFrame)

def test_quote_constructor_only():
    q = Quote(symbol="AAA", random_agent=False, show_log=False)
    assert q.symbol == "AAA"

def test_trading_constructor_only():
    t = Trading(symbol="AAA", random_agent=False, show_log=False)
    assert t.symbol == "AAA"
