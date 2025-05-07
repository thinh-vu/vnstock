# pytest tests/test_explorer/1_smoke/test_smoke_tcbs.py --maxfail=1 -q

import pytest
import pandas as pd

from vnstock.explorer.tcbs.company import Company
from vnstock.explorer.tcbs.financial import Finance
from vnstock.explorer.tcbs.models import TickerModel
from vnstock.explorer.tcbs.quote import Quote
from vnstock.explorer.tcbs.screener import Screener
from vnstock.explorer.tcbs.trading import Trading

# Dummy HTTP response for requests.get (if ever used)
class DummyGetResp:
    status_code = 200
    def json(self):
        return {"data": []}

@pytest.fixture(autouse=True)
def patch_external_calls(monkeypatch):
    # Patch client.send_request (used by Company, Finance, Screener, Trading)
    monkeypatch.setattr(
        "vnstock.core.utils.client.send_request",
        lambda *args, **kwargs: {
            # include both keys for screener and trading
            "searchData": {"pageContent": []},
            "data": []
        }
    )
    # Patch requests.get for Quote.history/intraday
    monkeypatch.setattr("requests.get", lambda *a, **k: DummyGetResp())
    yield

def test_company_instantiation():
    c = Company(symbol="AAA", random_agent=False, to_df=True, show_log=False)
    assert isinstance(c, Company)

def test_finance_balance_sheet_returns_df():
    f = Finance(symbol="AAA", report_type="balance_sheet", period="year", get_all=False, show_log=False)
    # Should return an (empty) DataFrame without error
    df = f.balance_sheet(period="year", to_df=True, show_log=False)
    assert isinstance(df, pd.DataFrame)

def test_ticker_model_validation():
    tm = TickerModel(symbol="AAA", start="2025-01-01", end=None, interval="1D")
    assert tm.symbol == "AAA"
    assert tm.interval == "1D"

def test_quote_instantiation():
    q = Quote(symbol="AAA", random_agent=False, show_log=False)
    assert q.symbol == "AAA"

def test_screener_stock_returns_df():
    sc = Screener(random_agent=False, show_log=False)
    df = sc.stock(params={"exchangeName": "HOSE"}, limit=5, id=None, lang="vi")
    assert isinstance(df, pd.DataFrame)

def test_trading_price_board_returns_df():
    t = Trading(symbol="AAA", random_agent=False, show_log=False)
    df = t.price_board(symbol_ls=["AAA"], std_columns=True, to_df=True, show_log=False)
    assert isinstance(df, pd.DataFrame)
