import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from vnstock.common.data.data_explorer import (
    StockComponents, MSNComponents, Quote, Listing, 
    Trading, Company, Finance, Screener, Fund
)

# Configure logging
VERBOSE_TESTING = False  # Set to True for detailed debug output
if not VERBOSE_TESTING:
    logging.getLogger('vnstock').setLevel(logging.ERROR)

class BaseTestCase(unittest.TestCase):
    """Base class with helper methods for all test cases"""
    
    def _create_price_mock_data(self, rows=30, base_price=1000, volatility=100):
        """Create consistent mock data for price history tests"""
        return pd.DataFrame({
            'time': pd.date_range(start='2023-01-01', periods=rows),
            'open': np.random.rand(rows) * volatility + base_price,
            'high': np.random.rand(rows) * volatility + base_price + 10,
            'low': np.random.rand(rows) * volatility + base_price - 10,
            'close': np.random.rand(rows) * volatility + base_price,
            'volume': np.random.randint(100000, 1000000, rows)
        })

    def _setup_history_mock(self, mock_import, rows=30, base_price=1000):
        """Set up a mock for history calls"""
        mock_module = MagicMock()
        mock_import.return_value = mock_module
        mock_data = self._create_price_mock_data(rows, base_price)
        mock_module.Quote.return_value.history = MagicMock(return_value=mock_data)
        return mock_module, mock_data

class TestVnstockDataSources(BaseTestCase):
    """Test for data sources initialization and validation"""
    
    def test_invalid_source(self):
        """Test that invalid data sources raise appropriate errors"""
        with self.assertRaises(ValueError):
            StockComponents(symbol='ACB', source='INVALID')
        
        with self.assertRaises(ValueError):
            MSNComponents(symbol='EURUSD', source='INVALID')

class TestStockData(BaseTestCase):
    """Tests for stock data retrieval from multiple sources"""
    
    def setUp(self):
        self.vci_stock = StockComponents(symbol='ACB', source='VCI')
        self.tcbs_stock = StockComponents(symbol='ACB', source='TCBS')
        
    def test_stock_initialization(self):
        """Test proper initialization of stock components with different sources"""
        self.assertEqual(self.vci_stock.symbol, 'ACB')
        self.assertEqual(self.vci_stock.source, 'VCI')
        self.assertEqual(self.tcbs_stock.symbol, 'ACB')
        self.assertEqual(self.tcbs_stock.source, 'TCBS')
        
        # Verify all expected components are initialized
        for stock in [self.vci_stock, self.tcbs_stock]:
            self.assertIsNotNone(stock.quote)
            self.assertIsNotNone(stock.listing)
            self.assertIsNotNone(stock.trading)
            self.assertIsNotNone(stock.company)
            self.assertIsNotNone(stock.finance)
    
    def test_stock_update_symbol(self):
        """Test updating symbol updates all sub-components"""
        self.vci_stock.update_symbol('VCB')
        self.assertEqual(self.vci_stock.symbol, 'VCB')
        self.assertEqual(self.vci_stock.quote.symbol, 'VCB')
        self.assertEqual(self.vci_stock.company.symbol, 'VCB')
        self.assertEqual(self.vci_stock.finance.symbol, 'VCB')
    
    @patch('vnstock.common.data.data_explorer.importlib.import_module')
    def test_stock_history(self, mock_import):
        """Test stock price history retrieval"""
        # Setup mock data
        mock_module, mock_data = self._setup_history_mock(mock_import)
        
        # Test with different parameters
        result = self.vci_stock.quote.history(
            start='2025-01-02', 
            end='2025-03-20'
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        
        # Check that the row count matches expected
        expected_rows = len(mock_data)
        actual_rows = len(result)
        self.assertEqual(actual_rows, expected_rows, 
                         f"Expected {expected_rows} rows but got {actual_rows}")
        
        # Check expected columns
        expected_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"Missing column: {col}")
    
    @patch('vnstock.common.data.data_explorer.importlib.import_module')
    def test_company_info(self, mock_import):
        """Test company information retrieval"""
        mock_module = MagicMock()
        mock_import.return_value = mock_module
        mock_module.Company.return_value.overview.return_value = {
            'name': 'Asia Commercial Joint Stock Bank',
            'industry': 'Banking'
        }
        
        result = self.tcbs_stock.company.overview()
        self.assertIsInstance(result, dict)
        self.assertEqual(result['name'], 'Asia Commercial Joint Stock Bank')

class TestDelistedSymbolsData(BaseTestCase):
    """Tests for handling delisted symbols data"""
    
    def setUp(self):
        # Initialize with delisted symbols
        self.vfmvf4 = StockComponents(symbol='VFMVF4', source='VCI')
        self.vis = StockComponents(symbol='VIS', source='VCI')
        self.vtp = StockComponents(symbol='VTP', source='VCI')
    
    def test_delisted_symbol_initialization(self):
        """Test initialization with delisted symbols doesn't fail"""
        self.assertEqual(self.vfmvf4.symbol, 'VFMVF4')
        self.assertEqual(self.vis.symbol, 'VIS')
        self.assertEqual(self.vtp.symbol, 'VTP')
    
    @patch('vnstock.common.data.data_explorer.importlib.import_module')
    def test_delisted_historical_data(self, mock_import):
        """Test retrieving historical data for delisted symbols before delisting"""
        # Setup mock data
        mock_module, mock_data = self._setup_history_mock(mock_import, rows=30, base_price=20)
        
        # Test with VFMVF4
        result = self.vfmvf4.quote.history(
            start='2010-01-01', 
            end='2010-01-30'
        )
        
        # For delisted symbols, we just verify the data structure, not exact content
        self.assertIsInstance(result, pd.DataFrame)
        
        # Check expected columns
        expected_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"Missing column: {col}")
    
    @patch('vnstock.common.data.data_explorer.importlib.import_module')
    def test_empty_recent_data(self, mock_import):
        """Test retrieving recent data for delisted symbols returns empty dataset"""
        mock_module = MagicMock()
        mock_import.return_value = mock_module
        
        # Empty DataFrame for recent data for delisted symbol
        empty_data = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        mock_module.Quote.return_value.history.return_value = empty_data
        
        result = self.vis.quote.history(
            start='2023-01-01', 
            end='2023-01-30'
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 0)
    
    @patch('vnstock.common.data.data_explorer.importlib.import_module')
    def test_api_error_handling(self, mock_import):
        """Test error handling for delisted symbols when API returns error"""
        mock_module = MagicMock()
        mock_import.return_value = mock_module
        
        # Simulate API error for delisted symbol
        error_message = "Symbol VTP not found or has been delisted"
        mock_module.Quote.return_value.history.side_effect = ValueError(error_message)
        
        with self.assertRaises(ValueError) as context:
            self.vtp.quote.history(
                start='2023-01-01', 
                end='2023-01-30'
            )
        
        self.assertEqual(str(context.exception), error_message)

class TestFuturesData(BaseTestCase):
    """Tests for futures data retrieval"""
    
    def setUp(self):
        # Initialize with VN30F1M (current month VN30 futures)
        self.futures = StockComponents(symbol='VN30F1M', source='VCI')
    
    def test_futures_initialization(self):
        """Test proper initialization of futures components"""
        self.assertEqual(self.futures.symbol, 'VN30F1M')
        self.assertEqual(self.futures.source, 'VCI')
        self.assertIsNotNone(self.futures.quote)
    
    @patch('vnstock.common.data.data_explorer.importlib.import_module')
    def test_futures_history(self, mock_import):
        """Test futures price history retrieval"""
        # Setup mock
        mock_module, mock_data = self._setup_history_mock(
            mock_import, rows=30, base_price=1200
        )
        
        # Test VN30F1M
        result = self.futures.quote.history(
            start='2023-01-01', 
            end='2023-01-30'
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        
        # Check that the row count matches expected
        expected_rows = len(mock_data)
        actual_rows = len(result)
        self.assertEqual(actual_rows, expected_rows, 
                         f"Expected {expected_rows} rows but got {actual_rows}")
        
        # Test other future contracts
        contracts = ['VN30F2504', 'VN30F2403']
        for contract in contracts:
            result = self.futures.quote.history(
                symbol=contract,
                start='2023-01-01', 
                end='2023-01-30'
            )
            self.assertIsInstance(result, pd.DataFrame)

class TestIndexData(BaseTestCase):
    """Tests for market index data retrieval"""
    
    def setUp(self):
        self.vci_index = StockComponents(symbol='VNINDEX', source='VCI')
        self.msn_index = MSNComponents(symbol='DJI', source='MSN')
    
    def test_index_initialization(self):
        """Test proper initialization of index components"""
        self.assertEqual(self.vci_index.symbol, 'VNINDEX')
        self.assertEqual(self.vci_index.source, 'VCI')
        self.assertEqual(self.msn_index.symbol, 'DJI')
        self.assertEqual(self.msn_index.source, 'MSN')
    
    @patch('vnstock.common.data.data_explorer.importlib.import_module')
    def test_local_index_history(self, mock_import):
        """Test local market index history retrieval"""
        try:
            # Setup mock
            mock_module, mock_data = self._setup_history_mock(
                mock_import, rows=30, base_price=1000
            )
            
            # Test VNINDEX
            result = self.vci_index.quote.history(
                start='2023-01-01', 
                end='2023-01-30'
            )
            
            self.assertIsInstance(result, pd.DataFrame)
            
            # Check that the row count matches expected
            expected_rows = len(mock_data)
            actual_rows = len(result)
            self.assertEqual(actual_rows, expected_rows, 
                             f"Expected {expected_rows} rows but got {actual_rows}")
            
            # Test other indices
            indices = ['HNXINDEX', 'UPCOMINDEX']
            for index in indices:
                result = self.vci_index.quote.history(
                    symbol=index,
                    start='2023-01-01', 
                    end='2023-01-30'
                )
                self.assertIsInstance(result, pd.DataFrame)
                
        except Exception as e:
            self.fail(f"Test raised unexpected exception: {e}")
    
    @patch('vnstock.common.data.data_explorer.importlib.import_module')
    def test_global_index_history(self, mock_import):
        """Test global market index history retrieval"""
        # Setup mock
        mock_module, mock_data = self._setup_history_mock(
            mock_import, rows=30, base_price=35000
        )
        
        # Test DJI (Dow Jones)
        result = self.msn_index.quote.history(
            start='2023-01-01', 
            end='2023-01-30'
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), len(mock_data))

class TestForexData(BaseTestCase):
    """Tests for forex data retrieval from MSN"""
    
    def setUp(self):
        self.forex = MSNComponents(symbol='EURUSD', source='MSN')
    
    def test_forex_initialization(self):
        """Test proper initialization of forex components"""
        self.assertEqual(self.forex.symbol, 'EURUSD')
        self.assertEqual(self.forex.source, 'MSN')
        self.assertIsNotNone(self.forex.quote)
    
    @patch('vnstock.common.data.data_explorer.importlib.import_module')
    def test_forex_history(self, mock_import):
        """Test forex rate history retrieval"""
        # Setup mock
        mock_module, mock_data = self._setup_history_mock(
            mock_import, rows=30, base_price=1.1, volatility=0.05
        )
        
        # Test EURUSD
        result = self.forex.quote.history(
            start='2023-01-01', 
            end='2023-01-30'
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), len(mock_data))
        
        # Test JPYVND
        result = self.forex.quote.history(
            symbol='JPYVND',
            start='2023-01-01', 
            end='2023-01-30'
        )
        
        self.assertIsInstance(result, pd.DataFrame)

class TestCryptoData(BaseTestCase):
    """Tests for cryptocurrency data retrieval from MSN"""
    
    def setUp(self):
        self.crypto = MSNComponents(symbol='BTC', source='MSN')
    
    def test_crypto_initialization(self):
        """Test proper initialization of crypto components"""
        self.assertEqual(self.crypto.symbol, 'BTC')
        self.assertEqual(self.crypto.source, 'MSN')
        self.assertIsNotNone(self.crypto.quote)
    
    @patch('vnstock.common.data.data_explorer.importlib.import_module')
    def test_crypto_history(self, mock_import):
        """Test cryptocurrency price history retrieval"""
        # Setup mock
        mock_module, mock_data = self._setup_history_mock(
            mock_import, rows=30, base_price=30000, volatility=1000
        )
        
        # Test BTC
        result = self.crypto.quote.history(
            start='2023-01-01', 
            end='2023-01-30'
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), len(mock_data))

class TestCoveredWarrantData(BaseTestCase):
    """Tests for covered warrant data retrieval"""
    
    def setUp(self):
        self.cw = StockComponents(symbol='CFPT2314', source='VCI')
    
    def test_cw_initialization(self):
        """Test proper initialization of covered warrant components"""
        self.assertEqual(self.cw.symbol, 'CFPT2314')
        self.assertEqual(self.cw.source, 'VCI')
        self.assertIsNotNone(self.cw.quote)
    
    @patch('vnstock.common.data.data_explorer.importlib.import_module')
    def test_cw_history(self, mock_import):
        """Test covered warrant price history retrieval"""
        # Setup mock
        mock_module, mock_data = self._setup_history_mock(
            mock_import, rows=30, base_price=500, volatility=100
        )
        
        result = self.cw.quote.history(
            start='2023-01-01', 
            end='2023-01-30'
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), len(mock_data))

class TestBondData(BaseTestCase):
    """Tests for bond data retrieval"""
    
    def setUp(self):
        self.bond = StockComponents(symbol='CII424002', source='VCI')
    
    def test_bond_initialization(self):
        """Test proper initialization of bond components"""
        self.assertEqual(self.bond.symbol, 'CII424002')
        self.assertEqual(self.bond.source, 'VCI')
        self.assertIsNotNone(self.bond.quote)
    
    @patch('vnstock.common.data.data_explorer.importlib.import_module')
    def test_bond_history(self, mock_import):
        """Test bond price history retrieval"""
        # Setup mock with stable prices typical for bonds
        mock_module = MagicMock()
        mock_import.return_value = mock_module
        mock_data = pd.DataFrame({
            'time': pd.date_range(start='2023-01-01', periods=30),
            'open': np.ones(30) * 100000,
            'high': np.ones(30) * 100000,
            'low': np.ones(30) * 100000,
            'close': np.ones(30) * 100000,
            'volume': np.random.randint(100, 1000, 30)
        })
        mock_module.Quote.return_value.history.return_value = mock_data
        
        result = self.bond.quote.history(
            start='2023-01-01', 
            end='2023-01-30'
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), len(mock_data))

class TestErrorHandling(BaseTestCase):
    """Tests for error handling and edge cases"""
    
    def setUp(self):
        self.stock = StockComponents(symbol='ACB', source='VCI')
    
    @patch('vnstock.common.data.data_explorer.importlib.import_module')
    def test_nonexistent_symbol(self, mock_import):
        """Test behavior with nonexistent symbols"""
        mock_module = MagicMock()
        mock_import.return_value = mock_module
        mock_module.Quote.return_value.history.side_effect = ValueError("Symbol not found")
        
        with self.assertRaises(ValueError):
            self.stock.quote.history(symbol='NONEXISTENT')
    
    @patch('vnstock.common.data.data_explorer.importlib.import_module')
    def test_invalid_date_range(self, mock_import):
        """Test behavior with invalid date ranges"""
        mock_module = MagicMock()
        mock_import.return_value = mock_module
        mock_module.Quote.return_value.history.side_effect = ValueError("End date must be after start date")
        
        with self.assertRaises(ValueError):
            self.stock.quote.history(start='2023-01-30', end='2023-01-01')
    
    @patch('vnstock.common.data.data_explorer.importlib.import_module')
    def test_future_date(self, mock_import):
        """Test behavior with future dates"""
        mock_module = MagicMock()
        mock_import.return_value = mock_module
        
        # Set a future date
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Empty data for future dates
        mock_data = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        mock_module.Quote.return_value.history.return_value = mock_data
        
        result = self.stock.quote.history(
            start='2023-01-01', 
            end=future_date
        )
        
        # Should return an empty DataFrame for future dates
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 0)

class TestDataIntegrity(BaseTestCase):
    """Tests for data integrity and consistency"""
    
    @patch('vnstock.common.data.data_explorer.importlib.import_module')
    def test_stock_data_schema(self, mock_import):
        """Test stock data has the expected schema"""
        stock = StockComponents(symbol='ACB', source='VCI')
        
        mock_module = MagicMock()
        mock_import.return_value = mock_module
        
        # Create mock data with exact column names
        mock_data = pd.DataFrame({
            'time': pd.date_range(start='2023-01-01', periods=5),
            'open': [25000, 25100, 25200, 25300, 25400],
            'high': [25500, 25600, 25700, 25800, 25900],
            'low': [24800, 24900, 25000, 25100, 25200],
            'close': [25200, 25300, 25400, 25500, 25600],
            'volume': [1000000, 1100000, 1200000, 1300000, 1400000]
        })
        mock_module.Quote.return_value.history.return_value = mock_data
        
        result = stock.quote.history(start='2023-01-01', end='2023-01-05')
        
        # Check column presence one by one
        expected_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"Column '{col}' is missing from result")
        
        # Verify data types
        self.assertIsInstance(result['time'][0], pd.Timestamp)
        self.assertTrue(np.issubdtype(result['open'].dtype, np.number))
        
        # Verify high >= low
        self.assertTrue(all(result['high'] >= result['low']))
        
        # Verify high >= open and high >= close
        self.assertTrue(all(result['high'] >= result['open']))
        self.assertTrue(all(result['high'] >= result['close']))
        
        # Verify low <= open and low <= close
        self.assertTrue(all(result['low'] <= result['open']))
        self.assertTrue(all(result['low'] <= result['close']))

if __name__ == '__main__':
    # Run with coverage
    import sys
    import coverage
    
    # Setup coverage
    cov = coverage.Coverage(
        source=['vnstock.common.data.data_explorer'],
        omit=['*/tests/*', '*/site-packages/*']
    )
    cov.start()
    
    # Run all tests or specific test classes
    if len(sys.argv) > 1:
        # Run specific test classes if provided
        test_classes = []
        for arg in sys.argv[1:]:
            if arg.startswith('Test'):
                test_classes.append(globals()[arg])
        
        for test_class in test_classes:
            unittest.TextTestRunner(verbosity=2).run(
                unittest.TestLoader().loadTestsFromTestCase(test_class)
            )
    else:
        # Run all tests
        test_suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
        unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # Generate coverage report
    cov.stop()
    cov.save()
    
    print("\nCoverage Summary:")
    cov.report()
    
    print("\nGenerating HTML coverage report in htmlcov directory...")
    cov.html_report(directory='htmlcov')
    
    print("\nCompleted test run with coverage analysis")
    
    # Exit with non-zero code if tests failed
    sys.exit(not unittest.TextTestRunner().run(test_suite).wasSuccessful())
