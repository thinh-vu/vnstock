import warnings
# Silence the openpyxl “no default style” warning
warnings.filterwarnings(
    "ignore",
    message="Workbook contains no default style, apply openpyxl's default"
)

import pytest
import pandas as pd

from vnstock.explorer.misc.exchange_rate import vcb_exchange_rate
from vnstock.explorer.misc.gold_price    import sjc_gold_price, btmc_goldprice

EMPTY_DF = pd.DataFrame()

@pytest.fixture(autouse=True)
def patch_misc(monkeypatch):
    # Stub out each misc function to always return an empty DataFrame
    monkeypatch.setattr(
        "vnstock.explorer.misc.exchange_rate.vcb_exchange_rate",
        lambda date='': EMPTY_DF
    )
    monkeypatch.setattr(
        "vnstock.explorer.misc.gold_price.sjc_gold_price",
        lambda date=None: EMPTY_DF
    )
    monkeypatch.setattr(
        "vnstock.explorer.misc.gold_price.btmc_goldprice",
        lambda url=None: EMPTY_DF
    )
    yield

def test_vcb_exchange_rate_returns_dataframe():
    df = vcb_exchange_rate(date="2025-05-07")
    assert isinstance(df, pd.DataFrame)

def test_sjc_gold_price_returns_dataframe():
    df = sjc_gold_price(date="2025-05-07")
    assert isinstance(df, pd.DataFrame)

def test_btmc_goldprice_returns_dataframe():
    df = btmc_goldprice()
    assert isinstance(df, pd.DataFrame)
