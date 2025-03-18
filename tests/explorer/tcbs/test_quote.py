import unittest
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta
import json
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from vnstock.explorer.tcbs.quote import Quote
from vnstock.explorer.tcbs.const import _INTERVAL_MAP, _INDEX_MAPPING

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
            with patch('vnstock.core.utils.parser.get_asset_type', return_value="derivative"):
                quote = Quote(symbol, show_log=False)
                self.assertEqual(quote.symbol, symbol)
                self.assertEqual(quote.asset_type, "derivative")
    
    @patch('vnstock.core.utils.parser.get_asset_type')
    def test_init_with_coverwarrant_symbol(self, mock_get_asset_type):
        """Test initialization with a coverwarrant symbol."""
        mock_get_asset_type.return_value = "coverwarrant"
        
        quote = Quote("CFPT2314", show_log=False)
        self.assertEqual(quote.symbol, "CFPT2314")
        self.assertEqual(quote.asset_type, "coverwarrant")
    
    @patch('vnstock.core.utils.parser.get_asset_type')
    def test_init_with_bond_symbol(self, mock_get_asset_type):
        """Test initialization with a bond symbol."""
        mock_get_asset_type.return_value = "bond"
        
        quote = Quote("CII424002", show_log=False)
        self.assertEqual(quote.symbol, "CII424002")
        self.assertEqual(quote.asset_type, "bond")
    
    @patch('vnstock.core.utils.parser.get_asset_type')
    def test_init_with_delisted_symbols(self, mock_get_asset_type):
        """Test initialization with delisted symbols."""
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
    
    @patch('requests.get')
    @patch('vnstock.core.utils.validation.validate_date_range')
    def test_history_with_valid_inputs(self, mock_validate_date_range, mock_get):
        """Test history method with valid inputs."""
        # Setup mocks
        mock_validate_date_range.return_value = ("2023-01-01", "2023-01-10")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': [{"data": "sample_data"}]}
        mock_get.return_value = mock_response
        
        # Mock data transformation
        with patch.object(self.quote, '_as_df') as mock_as_df:
            mock_df = pd.DataFrame({"date": ["2023-01-01"], "close": [100.0]})
            mock_as_df.return_value = mock_df
            
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
    
    @patch('requests.get')
    def test_history_with_all_intervals(self, mock_get):
        """Test history method with all valid intervals from _INTERVAL_MAP."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': [{"data": "sample_data"}]}
        mock_get.return_value = mock_response
        
        with patch.object(self.quote, '_as_df') as mock_as_df:
            mock_df = pd.DataFrame({"date": ["2023-01-01"], "close": [100.0]})
            mock_as_df.return_value = mock_df
            
            for interval in _INTERVAL_MAP.keys():
                result = self.quote.history("2023-01-01", "2023-01-10", interval=interval)
                self.assertTrue(isinstance(result, pd.DataFrame))
    
    @patch('requests.get')
    def test_history_json_output(self, mock_get):
        """Test history method with JSON output."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': [{"data": "sample_data"}]}
        mock_get.return_value = mock_response
        
        mock_df = pd.DataFrame({"date": ["2023-01-01"], "close": [100.0]})
        json_output = '[{"date":"2023-01-01","close":100.0}]'
        
        with patch.object(self.quote, '_as_df', return_value=mock_df):
            with patch.object(pd.DataFrame, 'to_json', return_value=json_output):
                result = self.quote.history("2023-01-01", "2023-01-10", to_df=False)
                self.assertEqual(result, json_output)
    
    @patch('requests.get')
    def test_history_with_count_back(self, mock_get):
        """Test history method with count_back parameter."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': [{"data": "sample_data"}]}
        mock_get.return_value = mock_response
        
        mock_df = pd.DataFrame({
            "date": ["2023-01-01", "2023-01-02", "2023-01-03"], 
            "close": [100.0, 101.0, 102.0]
        })
        
        with patch.object(self.quote, '_as_df', return_value=mock_df):
            result = self.quote.history("2023-01-01", "2023-01-10", count_back=2)
            # Verify URL contains the countBack parameter
            self.assertTrue("countBack=2" in mock_get.call_args[0][0])
    
    @patch('requests.get')
    def test_history_with_error_response(self, mock_get):
        """Test history method with error response."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        mock_get.return_value = mock_response
        
        with self.assertRaises(ConnectionError):
            self.quote.history("2023-01-01", "2023-01-10")
    
    @patch('vnstock.explorer.tcbs.quote.Quote._long_history')
    def test_history_with_long_date_range(self, mock_long_history):
        """Test history method with date range > 365 days."""
        mock_df = pd.DataFrame({"date": ["2023-01-01"], "close": [100.0]})
        mock_long_history.return_value = mock_df
        
        # Test with date range > 365 days
        start = "2022-01-01"
        end = "2023-01-10"  # More than 365 days later
        
        result = self.quote.history(start, end)
        self.assertTrue(isinstance(result, pd.DataFrame))
        mock_long_history.assert_called_once()
    
    def test_history_with_invalid_date_range(self):
        """Test history method with invalid date range."""
        with self.assertRaises(ValueError):
            self.quote.history("2023-01-10", "2023-01-01")  # End before start

class TestQuoteLongHistory(unittest.TestCase):
    """Test cases for the _long_history method."""
    
    def setUp(self):
        self.quote = Quote("ACV", show_log=False)
    
    @patch('vnstock.explorer.tcbs.quote.Quote.history')
    def test_long_history_single_chunk(self, mock_history):
        """Test _long_history method with a single year chunk."""
        mock_df = pd.DataFrame({
            "time": ["2023-01-01", "2023-02-01", "2023-03-01"],
            "close": [100.0, 101.0, 102.0]
        })
        mock_history.return_value = mock_df
        
        result = self.quote._long_history("2023-01-01", "2023-03-01", show_log=False)
        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assertEqual(len(result), 3)
        mock_history.assert_called_once()
    
    @patch('vnstock.explorer.tcbs.quote.Quote.history')
    def test_long_history_multiple_chunks(self, mock_history):
        """Test _long_history method with multiple year chunks."""
        # Create a different DataFrame for each call
        mock_df1 = pd.DataFrame({
            "time": ["2022-01-01", "2022-06-01"],
            "close": [100.0, 101.0]
        })
        mock_df2 = pd.DataFrame({
            "time": ["2023-01-01", "2023-06-01"],
            "close": [102.0, 103.0]
        })
        
        mock_history.side_effect = [mock_df1, mock_df2]
        
        result = self.quote._long_history("2022-01-01", "2023-06-01", show_log=False)
        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assertEqual(len(result), 4)  # Combined length of both DataFrames
        self.assertEqual(mock_history.call_count, 2)
    
    @patch('vnstock.explorer.tcbs.quote.Quote.history')
    def test_long_history_error_handling(self, mock_history):
        """Test _long_history method with error in one chunk."""
        # First call raises exception, second call succeeds
        mock_df = pd.DataFrame({
            "time": ["2023-01-01", "2023-06-01"],
            "close": [102.0, 103.0]
        })
        mock_history.side_effect = [Exception("Data not found"), mock_df]
        
        result = self.quote._long_history("2022-01-01", "2023-06-01", show_log=False)
        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assertEqual(len(result), 2)  # Only second DataFrame is returned
        self.assertEqual(mock_history.call_count, 2)
    
    @patch('vnstock.explorer.tcbs.quote.Quote.history')
    def test_long_history_no_data(self, mock_history):
        """Test _long_history method with no data for all chunks."""
        mock_history.side_effect = Exception("Data not found")
        
        with self.assertRaises(ValueError):
            self.quote._long_history("2022-01-01", "2023-06-01", show_log=False)

class TestQuoteIntraday(unittest.TestCase):
    """Test cases for the intraday method."""
    
    def setUp(self):
        self.quote = Quote("ACV", show_log=False)
    
    @patch('vnstock.core.utils.api_client.send_request')
    @patch('vnstock.core.utils.data_transform.intraday_to_df')
    def test_intraday_with_valid_inputs(self, mock_intraday_to_df, mock_send_request):
        """Test intraday method with valid inputs."""
        # Setup mocks
        mock_send_request.return_value = {"data": [{"data": "sample_data"}]}
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
                result = quote.intraday()
                self.assertTrue(isinstance(result, pd.DataFrame))
    
    @patch('vnstock.core.utils.api_client.send_request')
    @patch('vnstock.core.utils.data_transform.intraday_to_df')
    def test_intraday_json_output(self, mock_intraday_to_df, mock_send_request):
        """Test intraday method with JSON output."""
        mock_send_request.return_value = {"data": [{"data": "sample_data"}]}
        mock_df = pd.DataFrame({"time": ["14:30:00"], "price": [100.0]})
        mock_intraday_to_df.return_value = mock_df
        json_output = '[{"time":"14:30:00","price":100.0}]'
        
        with patch.object(pd.DataFrame, 'to_json', return_value=json_output):
            result = self.quote.intraday(to_df=False)
            self.assertEqual(result, json_output)
    
    @patch('vnstock.core.utils.api_client.send_request')
    @patch('vnstock.core.utils.data_transform.intraday_to_df')
    def test_intraday_with_pagination(self, mock_intraday_to_df, mock_send_request):
        """Test intraday method with pagination."""
        # Setup mocks for multiple pages
        mock_send_request.side_effect = [
            {"data": [{"id": 1}]},
            {"data": [{"id": 2}]}
        ]
        
        # Combined data from both pages
        mock_df = pd.DataFrame({"time": ["14:30:00", "14:31:00"], "price": [100.0, 101.0]})
        mock_intraday_to_df.return_value = mock_df
        
        # Test with page_size requiring multiple requests
        result = self.quote.intraday(page_size=101)  # Requires 2 requests (100 + 1)
        
        # Verify both pages were requested
        self.assertEqual(mock_send_request.call_count, 2)
        
        # Verify parameters for first page
        first_call_params = mock_send_request.call_args_list[0][1]['params']
        self.assertEqual(first_call_params['page'], 0)
        self.assertEqual(first_call_params['size'], 100)
        
        # Verify parameters for second page
        second_call_params = mock_send_request.call_args_list[1][1]['params']
        self.assertEqual(second_call_params['page'], 1)
        self.assertEqual(second_call_params['size'], 1)
    
    @patch('vnstock.core.utils.api_client.send_request')
    @patch('vnstock.core.utils.data_transform.intraday_to_df')
    def test_intraday_with_custom_page(self, mock_intraday_to_df, mock_send_request):
        """Test intraday method with custom page parameter."""
        mock_send_request.return_value = {"data": [{"data": "sample_data"}]}
        mock_df = pd.DataFrame({"time": ["14:30:00"], "price": [100.0]})
        mock_intraday_to_df.return_value = mock_df
        
        result = self.quote.intraday(page=2)
        
        # Verify page parameter was passed correctly
        call_params = mock_send_request.call_args[1]['params']
        self.assertEqual(call_params['page'], 2)

class TestQuoteAsDf(unittest.TestCase):
    """Test cases for the _as_df method."""
    
    def setUp(self):
        self.quote = Quote("ACV", show_log=False)
    
    @patch('vnstock.core.utils.data_transform.ohlc_to_df')
    def test_as_df_conversion(self, mock_ohlc_to_df):
        """Test _as_df method for converting data to DataFrame."""
        mock_df = pd.DataFrame({
            "time": ["2023-01-01"],
            "open": [100.0],
            "high": [105.0],
            "low": [98.0],
            "close": [102.0],
            "volume": [1000000]
        })
        mock_ohlc_to_df.return_value = mock_df
        
        test_data = {"sample": "data"}
        result = self.quote._as_df(test_data, "stock")
        
        # Verify data_transform.ohlc_to_df was called with correct parameters
        mock_ohlc_to_df.assert_called_once_with(
            data=test_data,
            column_map=self.quote._OHLC_MAP,
            dtype_map=self.quote._OHLC_DTYPE,
            asset_type="stock",
            symbol=self.quote.symbol,
            source=self.quote.data_source,
            interval="1D"
        )
        
        self.assertEqual(result, mock_df)

def run_tests_with_coverage():
    """Run tests with coverage measurement."""
    import coverage
    
    # Start coverage measurement
    cov = coverage.Coverage(source=["vnstock.explorer.tcbs.quote"])
    cov.start()
    
    try:
        # Create and run test suite
        test_suite = unittest.TestSuite()
        test_suite.addTest(unittest.makeSuite(TestQuoteInitialization))
        test_suite.addTest(unittest.makeSuite(TestQuoteInputValidation))
        test_suite.addTest(unittest.makeSuite(TestQuoteHistory))
        test_suite.addTest(unittest.makeSuite(TestQuoteLongHistory))
        test_suite.addTest(unittest.makeSuite(TestQuoteIntraday))
        test_suite.addTest(unittest.makeSuite(TestQuoteAsDf))
        
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

# python3.10 -m pytest tests/explorer/tcbs/test_quote.py -v --cov=vnstock.explorer.tcbs.quote