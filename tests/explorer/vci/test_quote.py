import unittest
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import json
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from vnstock.explorer.vci.quote import Quote
from vnstock.explorer.vci.const import _INTERVAL_MAP, _INDEX_MAPPING

class TestQuoteInitialization(unittest.TestCase):
    """Test cases for the initialization of the Quote class."""
    
    def test_init_with_stock_symbol(self):
        """Test initialization with a stock symbol."""
        quote = Quote("ACV", show_log=False)
        self.assertEqual(quote.symbol, "ACV")
        self.assertEqual(quote.asset_type, "stock")
        
    def test_init_with_index_symbols(self):
        """Test initialization with index symbols."""
        # Test with uppercase, lowercase, and mapped values
        index_mapping = {'VNINDEX': 'VNINDEX', 'HNXINDEX': 'HNXIndex', 'UPCOMINDEX': 'HNXUpcomIndex'}
        
        for key, value in index_mapping.items():
            # Test with key as input
            quote = Quote(key, show_log=False)
            self.assertEqual(quote.symbol, value)
            self.assertEqual(quote.asset_type, "index")
            
            # Test with lowercase key
            quote = Quote(key.lower(), show_log=False)
            self.assertEqual(quote.symbol, value)
            self.assertEqual(quote.asset_type, "index")
    
    def test_init_with_derivative_symbols(self):
        """Test initialization with derivative symbols."""
        for symbol in ["VN30F1M", "VN30F2504"]:
            quote = Quote(symbol, show_log=False)
            self.assertEqual(quote.symbol, symbol)
            self.assertEqual(quote.asset_type, "derivative")
    
    @patch('vnstock.core.utils.parser.get_asset_type')
    def test_init_with_coverwarrant_symbol(self, mock_get_asset_type):
        """Test initialization with a coverwarrant symbol."""
        # Mock the asset type detection
        mock_get_asset_type.return_value = "coverwarrant"
        
        quote = Quote("CFPT2314", show_log=False)
        self.assertEqual(quote.symbol, "CFPT2314")
        self.assertEqual(quote.asset_type, "coverwarrant")
    
    @patch('vnstock.core.utils.parser.get_asset_type')
    def test_init_with_bond_symbol(self, mock_get_asset_type):
        """Test initialization with a bond symbol."""
        # Mock the asset type detection
        mock_get_asset_type.return_value = "bond"
        
        quote = Quote("CII424002", show_log=False)
        self.assertEqual(quote.symbol, "CII424002")
        self.assertEqual(quote.asset_type, "bond")
    
    @patch('vnstock.core.utils.parser.get_asset_type')
    def test_init_with_delisted_symbols(self, mock_get_asset_type):
        """Test initialization with delisted symbols."""
        # Mock the asset type detection for stock
        mock_get_asset_type.return_value = "stock"
        
        # Test delisted stock
        quote = Quote("ENF", show_log=False)
        self.assertEqual(quote.symbol, "ENF")
        self.assertEqual(quote.asset_type, "stock")
        
        # Test delisted ETF
        quote = Quote("VFMVF4", show_log=False)
        self.assertEqual(quote.symbol, "VFMVF4")
        self.assertEqual(quote.asset_type, "stock")

class TestQuoteInputValidation(unittest.TestCase):
    """Test cases for input validation in the Quote class."""
    
    def setUp(self):
        self.quote = Quote("ACV", show_log=False)
    
    def test_valid_interval(self):
        """Test all valid interval inputs from _INTERVAL_MAP."""
        for interval in _INTERVAL_MAP.keys():
            ticker = self.quote._input_validation("2023-01-01", "2023-01-10", interval)
            self.assertEqual(ticker.interval, interval)
    
    @patch('vnstock.core.utils.validation.validate_interval')
    def test_invalid_interval(self, mock_validate):
        """Test invalid interval inputs."""
        mock_validate.side_effect = ValueError("Invalid interval")
        
        with self.assertRaises(ValueError):
            self.quote._input_validation("2023-01-01", "2023-01-10", "invalid_interval")

class TestQuoteHistory(unittest.TestCase):
    """Test cases for the history method."""
    
    def setUp(self):
        self.quote = Quote("ACV", show_log=False)
    
    @patch('vnstock.core.utils.api_client.send_request')
    @patch('vnstock.core.utils.validation.convert_to_timestamps')
    @patch('vnstock.core.utils.validation.validate_date_range')
    @patch('vnstock.core.utils.data_transform.ohlc_to_df')
    def test_history_with_valid_inputs(self, mock_ohlc_to_df, mock_validate_date_range, 
                                       mock_convert_timestamps, mock_send_request):
        """Test history method with valid inputs."""
        # Setup mocks
        mock_validate_date_range.return_value = ("2023-01-01", "2023-01-10")
        mock_convert_timestamps.return_value = (1672531200000, 1673308800000)
        mock_send_request.return_value = [{"data": "sample_data"}]
        mock_df = pd.DataFrame({"date": ["2023-01-01"], "close": [100.0]})
        mock_ohlc_to_df.return_value = mock_df
        
        # Test with different symbols and asset types
        symbol_asset_pairs = [
            ("ACV", "stock"),
            ("QNS", "stock"),
            ("VNINDEX", "index"),
            ("VN30F1M", "derivative"),
            ("CFPT2314", "coverwarrant"),
            ("CII424002", "bond")
        ]
        
        for symbol, asset_type in symbol_asset_pairs:
            with patch('vnstock.core.utils.parser.get_asset_type', return_value=asset_type):
                quote = Quote(symbol, show_log=False)
                result = quote.history("2023-01-01", "2023-01-10", interval="1D")
                self.assertTrue(isinstance(result, pd.DataFrame))
    
    @patch('vnstock.core.utils.api_client.send_request')
    def test_history_with_all_intervals(self, mock_send_request):
        """Test history method with all valid intervals from _INTERVAL_MAP."""
        mock_df = pd.DataFrame({"date": ["2023-01-01"], "close": [100.0]})
        mock_send_request.return_value = [{"data": "sample_data"}]
        
        with patch('vnstock.core.utils.data_transform.ohlc_to_df', return_value=mock_df):
            for interval in _INTERVAL_MAP.keys():
                result = self.quote.history("2023-01-01", "2023-01-10", interval=interval)
                self.assertTrue(isinstance(result, pd.DataFrame))
    
    @patch('vnstock.core.utils.api_client.send_request')
    def test_history_json_output(self, mock_send_request):
        """Test history method with JSON output."""
        mock_df = pd.DataFrame({"date": ["2023-01-01"], "close": [100.0]})
        mock_send_request.return_value = [{"data": "sample_data"}]
        json_output = '[{"date":"2023-01-01","close":100.0}]'
        
        with patch('vnstock.core.utils.data_transform.ohlc_to_df', return_value=mock_df):
            with patch.object(pd.DataFrame, 'to_json', return_value=json_output):
                result = self.quote.history("2023-01-01", "2023-01-10", to_df=False)
                self.assertEqual(result, json_output)
    
    @patch('vnstock.core.utils.api_client.send_request')
    def test_history_with_count_back(self, mock_send_request):
        """Test history method with count_back parameter."""
        mock_df = pd.DataFrame({
            "date": ["2023-01-01", "2023-01-02", "2023-01-03"], 
            "close": [100.0, 101.0, 102.0]
        })
        mock_send_request.return_value = [{"data": "sample_data"}]
        
        with patch('vnstock.core.utils.data_transform.ohlc_to_df', return_value=mock_df):
            result = self.quote.history("2023-01-01", "2023-01-10", count_back=2)
            self.assertEqual(len(result), 2)
    
    @patch('vnstock.core.utils.api_client.send_request')
    def test_history_with_empty_data(self, mock_send_request):
        """Test history method with empty data response."""
        mock_send_request.return_value = None
        
        with self.assertRaises(ValueError):
            self.quote.history("2023-01-01", "2023-01-10")

class TestQuoteIntraday(unittest.TestCase):
    """Test cases for the intraday method."""
    
    def setUp(self):
        self.quote = Quote("ACV", show_log=False)
    
    @patch('vnstock.explorer.vci.listing.Listing.all_future_indices')
    @patch('vnstock.core.utils.api_client.send_request')
    @patch('vnstock.core.utils.data_transform.intraday_to_df')
    def test_intraday_with_valid_inputs(self, mock_intraday_to_df, mock_send_request, mock_all_future_indices):
        """Test intraday method with valid inputs."""
        # Setup mocks
        mock_all_future_indices.return_value = pd.Series(["VN30F1M", "VN30F2504"])
        mock_send_request.return_value = {"data": "sample_data"}
        mock_df = pd.DataFrame({"time": ["14:30:00"], "price": [100.0]})
        mock_intraday_to_df.return_value = mock_df
        
        # Test with different asset types
        symbol_asset_pairs = [
            ("ACV", "stock"),
            ("QNS", "stock"),
            ("VNINDEX", "index"),
            ("VN30F1M", "derivative"),
            ("CFPT2314", "coverwarrant"),
            ("CII424002", "bond")
        ]
        
        for symbol, asset_type in symbol_asset_pairs:
            with patch('vnstock.core.utils.parser.get_asset_type', return_value=asset_type):
                quote = Quote(symbol, show_log=False)
                # Skip derivatives that aren't in the support list
                if asset_type == "derivative" and symbol not in ["VN30F1M", "VN30F2504"]:
                    continue
                result = quote.intraday()
                self.assertTrue(isinstance(result, pd.DataFrame))
    
    @patch('vnstock.explorer.vci.listing.Listing.all_future_indices')
    @patch('vnstock.core.utils.api_client.send_request')
    @patch('vnstock.core.utils.data_transform.intraday_to_df')
    def test_intraday_json_output(self, mock_intraday_to_df, mock_send_request, mock_all_future_indices):
        """Test intraday method with JSON output."""
        mock_all_future_indices.return_value = pd.Series(["VN30F1M", "VN30F2504"])
        mock_df = pd.DataFrame({"time": ["14:30:00"], "price": [100.0]})
        mock_send_request.return_value = {"data": "sample_data"}
        mock_intraday_to_df.return_value = mock_df
        json_output = '[{"time":"14:30:00","price":100.0}]'
        
        with patch.object(pd.DataFrame, 'to_json', return_value=json_output):
            result = self.quote.intraday(to_df=False)
            self.assertEqual(result, json_output)
    
    @patch('vnstock.explorer.vci.listing.Listing.all_future_indices')
    @patch('vnstock.core.utils.parser.get_asset_type')
    def test_intraday_with_derivative_not_in_support_list(self, mock_get_asset_type, mock_all_future_indices):
        """Test intraday method with unsupported derivative symbol."""
        mock_all_future_indices.return_value = pd.Series(["VN30F1M", "VN30F2504"])
        mock_get_asset_type.return_value = "derivative"
        
        quote = Quote("UNSUPPORTED", show_log=False)
        
        with self.assertRaises(ValueError):
            quote.intraday()
    
    @patch('vnstock.explorer.vci.listing.Listing.all_future_indices')
    @patch('vnstock.core.utils.api_client.send_request')
    @patch('vnstock.core.utils.data_transform.intraday_to_df')
    def test_intraday_with_last_time(self, mock_intraday_to_df, mock_send_request, mock_all_future_indices):
        """Test intraday method with last_time parameter."""
        mock_all_future_indices.return_value = pd.Series(["VN30F1M", "VN30F2504"])
        mock_df = pd.DataFrame({"time": ["14:30:00"], "price": [100.0]})
        mock_send_request.return_value = {"data": "sample_data"}
        mock_intraday_to_df.return_value = mock_df
        
        result = self.quote.intraday(last_time="2023-01-01 14:30:00")
        self.assertTrue(isinstance(result, pd.DataFrame))
        
        # Verify request parameter
        expected_time = int(datetime.strptime("2023-01-01 14:30:00", "%Y-%m-%d %H:%M:%S").timestamp())
        self.assertEqual(mock_send_request.call_args[1]['payload']['truncTime'], expected_time)
    
    @patch('vnstock.explorer.vci.listing.Listing.all_future_indices')
    def test_intraday_with_invalid_last_time(self, mock_all_future_indices):
        """Test intraday method with invalid last_time format."""
        mock_all_future_indices.return_value = pd.Series(["VN30F1M", "VN30F2504"])
        
        with self.assertRaises(ValueError):
            self.quote.intraday(last_time="invalid_format")

class TestQuotePriceDepth(unittest.TestCase):
    """Test cases for the price_depth method."""
    
    def setUp(self):
        self.quote = Quote("ACV", show_log=False)
    
    @patch('vnstock.explorer.vci.listing.Listing.all_future_indices')
    @patch('vnstock.core.utils.api_client.send_request')
    def test_price_depth_with_valid_inputs(self, mock_send_request, mock_all_future_indices):
        """Test price_depth method with valid inputs."""
        mock_all_future_indices.return_value = pd.Series(["VN30F1M", "VN30F2504"])
        sample_data = [{"price": 100.0, "volume": 1000}]
        mock_send_request.return_value = sample_data
        
        # Test with different asset types
        symbol_asset_pairs = [
            ("ACV", "stock"),
            ("QNS", "stock"),
            ("VNINDEX", "index"),
            ("VN30F1M", "derivative"),
            ("CFPT2314", "coverwarrant"),
            ("CII424002", "bond")
        ]
        
        with patch.object(pd.DataFrame, 'rename'):
            for symbol, asset_type in symbol_asset_pairs:
                with patch('vnstock.core.utils.parser.get_asset_type', return_value=asset_type):
                    quote = Quote(symbol, show_log=False)
                    # Skip derivatives that aren't in the support list
                    if asset_type == "derivative" and symbol not in ["VN30F1M", "VN30F2504"]:
                        continue
                    result = quote.price_depth()
                    self.assertTrue(isinstance(result, pd.DataFrame))
    
    @patch('vnstock.explorer.vci.listing.Listing.all_future_indices')
    @patch('vnstock.core.utils.api_client.send_request')
    def test_price_depth_json_output(self, mock_send_request, mock_all_future_indices):
        """Test price_depth method with JSON output."""
        mock_all_future_indices.return_value = pd.Series(["VN30F1M", "VN30F2504"])
        sample_data = [{"price": 100.0, "volume": 1000}]
        mock_send_request.return_value = sample_data
        json_output = '[{"price":100.0,"volume":1000}]'
        
        with patch.object(pd.DataFrame, 'rename'):
            with patch.object(pd.DataFrame, 'to_json', return_value=json_output):
                result = self.quote.price_depth(to_df=False)
                self.assertEqual(result, json_output)
    
    @patch('vnstock.explorer.vci.listing.Listing.all_future_indices')
    @patch('vnstock.core.utils.parser.get_asset_type')
    def test_price_depth_with_derivative_not_in_support_list(self, mock_get_asset_type, mock_all_future_indices):
        """Test price_depth method with unsupported derivative symbol."""
        mock_all_future_indices.return_value = pd.Series(["VN30F1M", "VN30F2504"])
        mock_get_asset_type.return_value = "derivative"
        
        quote = Quote("UNSUPPORTED", show_log=False)
        
        with self.assertRaises(ValueError):
            quote.price_depth()

class TestQuote(unittest.TestCase):
    def setUp(self):
        self.symbol = 'VIC'
        self.quote = Quote(self.symbol)

    def test_init_with_default_headers(self):
        """Test khởi tạo Quote với headers mặc định"""
        self.assertEqual(self.quote.symbol, self.symbol.upper())
        self.assertEqual(self.quote.data_source, 'VCI')
        self.assertIn('User-Agent', self.quote.headers)
        self.assertIn('Referer', self.quote.headers)
        self.assertIn('Origin', self.quote.headers)
        self.assertEqual(
            self.quote.headers['Referer'], 
            'https://trading.vietcap.com.vn/'
        )
        self.assertEqual(
            self.quote.headers['Origin'], 
            'https://trading.vietcap.com.vn/'
        )

    def test_init_with_random_agent(self):
        """Test khởi tạo Quote với random_agent=True"""
        quote = Quote(self.symbol, random_agent=True)
        self.assertIn('User-Agent', quote.headers)
        # Kiểm tra User-Agent có chứa thông tin browser
        browsers = ['chrome', 'safari', 'firefox', 'coccoc', 'brave', 'vivaldi']
        self.assertTrue(
            any(browser in quote.headers['User-Agent'].lower() 
                for browser in browsers)
        )

    @patch('vnstock.core.utils.user_agent.get_headers')
    def test_init_with_custom_headers(self, mock_get_headers):
        """Test khởi tạo Quote với custom headers"""
        custom_headers = {
            'User-Agent': 'Custom Agent',
            'Referer': 'https://custom.com',
            'Origin': 'https://custom.com'
        }
        mock_get_headers.return_value = custom_headers
        
        quote = Quote(self.symbol)
        self.assertEqual(quote.headers, custom_headers)

    def test_init_with_show_log_false(self):
        """Test khởi tạo Quote với show_log=False"""
        quote = Quote(self.symbol, show_log=False)
        self.assertFalse(quote.show_log)

    def test_init_with_index_symbol(self):
        """Test khởi tạo Quote với mã index"""
        index_symbol = 'VNINDEX'
        quote = Quote(index_symbol)
        self.assertEqual(quote.symbol, 'VNINDEX')

def run_tests_with_coverage():
    """Run tests with coverage measurement."""
    import coverage
    
    # Start coverage measurement properly
    cov = coverage.Coverage(source=["vnstock.explorer.vci.quote"])
    cov.start()
    
    try:
        # Create and run test suite
        test_suite = unittest.TestSuite()
        test_suite.addTest(unittest.makeSuite(TestQuoteInitialization))
        test_suite.addTest(unittest.makeSuite(TestQuoteInputValidation))
        test_suite.addTest(unittest.makeSuite(TestQuoteHistory))
        test_suite.addTest(unittest.makeSuite(TestQuoteIntraday))
        test_suite.addTest(unittest.makeSuite(TestQuotePriceDepth))
        test_suite.addTest(unittest.makeSuite(TestQuote))
        
        test_runner = unittest.TextTestRunner(verbosity=2)
        test_result = test_runner.run(test_suite)
        
        return test_result.wasSuccessful()
    finally:
        # Ensure coverage is properly stopped
        cov.stop()
        cov.save()
        
        # Print coverage report
        print("\nCoverage Report:")
        cov.report()
        
        # Generate HTML report
        cov.html_report(directory='htmlcov')
        print("HTML coverage report generated in 'htmlcov' directory.")

if __name__ == '__main__':
    success = run_tests_with_coverage()
    sys.exit(not success)


# python3.10 -m pytest tests/explorer/vci/test_quote.py -v --cov=vnstock.explorer.vci.quote