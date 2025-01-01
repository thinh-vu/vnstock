import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from vnstock.common.data.data_explorer import StockComponents, Quote, Listing, Trading, Company, Finance, MSNComponents
from vnstock.common.vnstock import Vnstock
from vnstock.explorer.msn.const import _CURRENCY_ID_MAP, _GLOBAL_INDICES, _CRYPTO_ID_MAP
msn_symbol_map = {**_CURRENCY_ID_MAP, **_GLOBAL_INDICES, **_CRYPTO_ID_MAP}

class TestVnstock(unittest.TestCase):

    def test_vnstock_init_valid_source(self):
        vnstock = Vnstock(source="VCI")
        self.assertEqual(vnstock.source, "VCI")

    def test_vnstock_init_invalid_source(self):
        with self.assertRaises(ValueError):
            Vnstock(source="INVALID")

    def test_vnstock_stock(self):
        vnstock = Vnstock(source="VCI")
        stock = vnstock.stock(symbol="ACB")
        self.assertIsInstance(stock, StockComponents)
        self.assertEqual(stock.symbol, "ACB")

    def test_vnstock_fx(self):
        vnstock = Vnstock(source="MSN")
        fx = vnstock.fx(symbol="EURUSD")
        self.assertIsInstance(fx, MSNComponents)
        self.assertEqual(fx.symbol, msn_symbol_map["EURUSD"].upper())

    def test_vnstock_crypto(self):
        vnstock = Vnstock(source="MSN")
        crypto = vnstock.crypto(symbol="BTC")
        self.assertIsInstance(crypto, MSNComponents)
        self.assertEqual(crypto.symbol, msn_symbol_map["BTC"].upper())

    def test_vnstock_world_index(self):
        vnstock = Vnstock(source="MSN")
        world_index = vnstock.world_index(symbol="DJI")
        self.assertIsInstance(world_index, MSNComponents)
        self.assertEqual(world_index.symbol, msn_symbol_map["DJI"].upper())


class TestStockComponents(unittest.TestCase):

    def test_stock_components_init_valid_source(self):
        stock = StockComponents(symbol="ACB", source="VCI")
        self.assertEqual(stock.symbol, "ACB")
        self.assertEqual(stock.source, "VCI")

    def test_stock_components_init_invalid_source(self):
        with self.assertRaises(ValueError):
            StockComponents(symbol="ACB", source="INVALID")

    def test_stock_components_update_symbol(self):
        stock = StockComponents(symbol="ACB", source="VCI")
        stock.update_symbol("ACB")
        self.assertEqual(stock.symbol, "ACB")

    def test_stock_components_update_invalid_symbol(self):
        stock = StockComponents(symbol="VN30F1M", source="VCI")
        stock.update_symbol("VN30F1M")
        self.assertEqual(stock.symbol, "VN30F1M")



class TestQuote(unittest.TestCase):

    def test_quote_init_valid_source(self):
        quote = Quote(symbol="VN30F1M", source="VCI")
        self.assertEqual(quote.symbol, "VN30F1M")
        self.assertEqual(quote.source, "VCI")

    def test_quote_init_invalid_source(self):
        with self.assertRaises(ValueError):
            Quote(symbol="VN30F1M", source="INVALID")

    @patch('vnstock.common.data.data_explorer.Quote._load_data_source')
    def test_quote_history(self, mock_load_data_source):
        # Mock the data source's history method
        mock_data_source = MagicMock()
        mock_history_data = pd.DataFrame({
            'time': ['2020-01-02', '2020-01-03', '2020-01-06', '2020-01-07'],
            'open': [877.5, 887.1, 877.5, 873.9],
            'high': [886.3, 887.9, 883.5, 877.8],
            'low': [876.5, 879.5, 871.6, 871.6],
            'close': [886.3, 879.5, 872.0, 875.0],
            'volume': [70480, 70389, 83770, 83997]
        })
        mock_data_source.history.return_value = mock_history_data
        mock_load_data_source.return_value = mock_data_source

        quote = Quote(symbol="VN30F1M", source="VCI")
        history = quote.history(start='2020-01-02', end='2024-05-25')

        # Assert that the returned DataFrame is equal to the expected DataFrame
        expected_history = pd.DataFrame({
            'time': ['2020-01-02', '2020-01-03', '2020-01-06', '2020-01-07'],
            'open': [877.5, 887.1, 877.5, 873.9],
            'high': [886.3, 887.9, 883.5, 877.8],
            'low': [876.5, 879.5, 871.6, 871.6],
            'close': [886.3, 879.5, 872.0, 875.0],
            'volume': [70480, 70389, 83770, 83997]
        })
        pd.testing.assert_frame_equal(history, expected_history)


class TestListing(unittest.TestCase):

    def test_listing_init_valid_source(self):
        listing = Listing(source="VCI")
        self.assertEqual(listing.source, "VCI")

    def test_listing_init_invalid_source(self):
        with self.assertRaises(ValueError):
            Listing(source="INVALID")

    def test_listing_all_symbols(self):
        listing = Listing(source="VCI")
        # Mock the data source's all_symbols method
        listing.data_source.all_symbols = lambda **kwargs: ["ACB", "VN30F1M"]
        symbols = listing.all_symbols()
        self.assertEqual(symbols, ["ACB", "VN30F1M"])


class TestTrading(unittest.TestCase):

    def test_trading_init_valid_source(self):
        trading = Trading(symbol="VN30F1M", source="VCI")
        self.assertEqual(trading.symbol, "VN30F1M")
        self.assertEqual(trading.source, "VCI")

    def test_trading_init_invalid_source(self):
        with self.assertRaises(ValueError):
            Trading(symbol="VN30F1M", source="INVALID")

    def test_trading_price_board(self):
        trading = Trading(symbol="VN30F1M", source="VCI")
        # Mock the data source's price_board method
        trading.data_source.price_board = lambda symbols_list, **kwargs: {"price_board": "data"}
        price_board = trading.price_board(symbols_list=["ACB", "VCB", "VIC", "FRT", "HAH"])
        self.assertEqual(price_board, {"price_board": "data"})


class TestCompany(unittest.TestCase):

    def test_company_init_valid_source(self):
        company = Company(symbol="ACB", source="TCBS")
        self.assertEqual(company.symbol, "ACB")

    def test_company_init_invalid_source(self):
        with self.assertRaises(ValueError):
            Company(symbol="ACB", source="INVALID")

    def test_company_profile(self):
        company = Company(symbol="ACB", source="TCBS")
        # Mock the data source's profile method
        company.data_source.profile = lambda **kwargs: {"profile": "data"}
        profile = company.profile()
        self.assertEqual(profile, {"profile": "data"})


class TestFinance(unittest.TestCase):

    def test_finance_init_valid_source(self):
        finance = Finance(symbol="ACB", source="TCBS")
        self.assertEqual(finance.symbol, "ACB")

    def test_finance_init_invalid_source(self):
        with self.assertRaises(ValueError):
            Finance(symbol="ACB", source="INVALID")

    def test_finance_balance_sheet(self):
        finance = Finance(symbol="ACB", source="TCBS")
        # Mock the data source's balance_sheet method
        finance.data_source.balance_sheet = lambda **kwargs: {"balance_sheet": "data"}
        balance_sheet = finance.balance_sheet()
        self.assertEqual(balance_sheet, {"balance_sheet": "data"})


class TestMSNComponents(unittest.TestCase):

    def test_msncomponents_init_valid_source(self):
        msn = MSNComponents(symbol="EURUSD", source="MSN")
        self.assertEqual(msn.symbol, "EURUSD")

    def test_msncomponents_init_invalid_source(self):
        with self.assertRaises(ValueError):
            MSNComponents(symbol="EURUSD", source="INVALID")

    def test_msncomponents_update_symbol(self):
        msn = MSNComponents(symbol="EURUSD", source="MSN")
        msn.update_symbol("USDJPY")
        self.assertEqual(msn.symbol, "USDJPY")


if __name__ == '__main__':
    unittest.main()
