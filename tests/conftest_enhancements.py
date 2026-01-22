"""
Enhanced pytest configuration for comprehensive testing.

This module extends conftest.py with additional fixtures and utilities
for performance testing, quality metrics, and advanced test scenarios.
"""

import pytest
import time
import psutil
import os
from typing import Dict, List, Callable, Any
from contextlib import contextmanager
import json
from pathlib import Path


# ============================================================================
# Performance Monitoring Fixtures
# ============================================================================

class PerformanceMonitor:
    """Monitor performance metrics during test execution."""
    
    def __init__(self):
        self.start_time = None
        self.start_memory = None
        self.metrics = {}
    
    def start(self):
        """Start monitoring."""
        self.start_time = time.time()
        self.start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
    
    def stop(self) -> Dict[str, float]:
        """Stop monitoring and return metrics."""
        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        
        return {
            'execution_time': end_time - self.start_time,
            'memory_used': end_memory - self.start_memory,
            'peak_memory': end_memory
        }


@pytest.fixture
def performance_monitor():
    """Provide performance monitoring capability."""
    return PerformanceMonitor()


@contextmanager
def measure_performance(test_name: str, threshold: float = None):
    """Context manager to measure test performance."""
    monitor = PerformanceMonitor()
    monitor.start()
    
    try:
        yield monitor
    finally:
        metrics = monitor.stop()
        if threshold and metrics['execution_time'] > threshold:
            pytest.warns(
                UserWarning,
                f"Test {test_name} exceeded threshold: "
                f"{metrics['execution_time']:.2f}s > {threshold}s"
            )


@pytest.fixture
def measure_perf():
    """Fixture to measure performance in tests."""
    return measure_performance


# ============================================================================
# Quality Metrics Fixtures
# ============================================================================

class QualityMetrics:
    """Track quality metrics during test execution."""
    
    def __init__(self):
        self.metrics = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'warnings': [],
        }
    
    def record_test(self, status: str, name: str, duration: float):
        """Record test result."""
        self.metrics['total_tests'] += 1
        self.metrics[status] += 1
    
    def add_error(self, error: str):
        """Add error to metrics."""
        self.metrics['errors'].append(error)
    
    def add_warning(self, warning: str):
        """Add warning to metrics."""
        self.metrics['warnings'].append(warning)
    
    def get_report(self) -> Dict:
        """Get quality report."""
        total = self.metrics['total_tests']
        return {
            'total_tests': total,
            'pass_rate': (self.metrics['passed'] / total * 100) if total > 0 else 0,
            'error_count': len(self.metrics['errors']),
            'warning_count': len(self.metrics['warnings']),
            'details': self.metrics
        }


@pytest.fixture
def quality_metrics():
    """Provide quality metrics tracking."""
    return QualityMetrics()


# ============================================================================
# Data Validation Fixtures
# ============================================================================

class DataValidator:
    """Comprehensive data validation utilities."""
    
    @staticmethod
    def validate_dataframe_schema(df, expected_schema: Dict[str, type]) -> List[str]:
        """Validate DataFrame schema against expected types."""
        errors = []
        
        for col, expected_type in expected_schema.items():
            if col not in df.columns:
                errors.append(f"Missing column: {col}")
            elif df[col].dtype != expected_type:
                errors.append(
                    f"Column {col}: expected {expected_type}, got {df[col].dtype}"
                )
        
        return errors
    
    @staticmethod
    def validate_data_ranges(df, ranges: Dict[str, tuple]) -> List[str]:
        """Validate numeric columns are within expected ranges."""
        errors = []
        
        for col, (min_val, max_val) in ranges.items():
            if col in df.columns:
                col_min = df[col].min()
                col_max = df[col].max()
                
                if col_min < min_val or col_max > max_val:
                    errors.append(
                        f"Column {col} out of range: "
                        f"[{col_min}, {col_max}] not in [{min_val}, {max_val}]"
                    )
        
        return errors
    
    @staticmethod
    def validate_no_nulls(df, columns: List[str]) -> List[str]:
        """Validate specified columns have no null values."""
        errors = []
        
        for col in columns:
            if col in df.columns:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    errors.append(f"Column {col} has {null_count} null values")
        
        return errors


@pytest.fixture
def data_validator():
    """Provide data validation utilities."""
    return DataValidator()


# ============================================================================
# API Response Validation Fixtures
# ============================================================================

class APIResponseValidator:
    """Validate API responses."""
    
    @staticmethod
    def validate_response_structure(response: Dict, required_keys: List[str]) -> List[str]:
        """Validate API response has required keys."""
        errors = []
        missing_keys = set(required_keys) - set(response.keys())
        
        if missing_keys:
            errors.append(f"Missing keys in response: {missing_keys}")
        
        return errors
    
    @staticmethod
    def validate_response_types(response: Dict, type_map: Dict[str, type]) -> List[str]:
        """Validate API response values have correct types."""
        errors = []
        
        for key, expected_type in type_map.items():
            if key in response:
                if not isinstance(response[key], expected_type):
                    errors.append(
                        f"Key {key}: expected {expected_type}, "
                        f"got {type(response[key])}"
                    )
        
        return errors


@pytest.fixture
def api_validator():
    """Provide API response validation utilities."""
    return APIResponseValidator()


# ============================================================================
# Test Report Generation Fixtures
# ============================================================================

class TestReportGenerator:
    """Generate comprehensive test reports."""
    
    def __init__(self, output_dir: str = "tests/report"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report = {
            'timestamp': None,
            'test_summary': {},
            'coverage': {},
            'performance': {},
            'quality': {}
        }
    
    def generate_json_report(self, filename: str = "test_report.json"):
        """Generate JSON test report."""
        report_path = self.output_dir / filename
        
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2, default=str)
        
        return report_path
    
    def generate_markdown_report(self, filename: str = "TEST_REPORT.md"):
        """Generate Markdown test report."""
        report_path = self.output_dir / filename
        
        with open(report_path, 'w') as f:
            f.write("# Test Report\n\n")
            f.write(f"Generated: {self.report['timestamp']}\n\n")
            
            f.write("## Test Summary\n")
            for key, value in self.report['test_summary'].items():
                f.write(f"- {key}: {value}\n")
            
            f.write("\n## Coverage\n")
            for key, value in self.report['coverage'].items():
                f.write(f"- {key}: {value}\n")
            
            f.write("\n## Performance\n")
            for key, value in self.report['performance'].items():
                f.write(f"- {key}: {value}\n")
        
        return report_path


@pytest.fixture
def report_generator():
    """Provide test report generation capability."""
    return TestReportGenerator()


# ============================================================================
# Mock Data Fixtures
# ============================================================================

@pytest.fixture
def mock_financial_data():
    """Mock financial report data."""
    return {
        'income_statement': {
            'item': ['Revenue', 'Cost of Goods Sold', 'Gross Profit'],
            'item_en': ['Revenue', 'Cost of Goods Sold', 'Gross Profit'],
            'item_id': ['revenue', 'cost_of_goods_sold', 'gross_profit'],
            '2024-Q1': [1000000, 600000, 400000],
            '2024-Q2': [1200000, 700000, 500000],
        },
        'balance_sheet': {
            'item': ['Total Assets', 'Total Liabilities', 'Total Equity'],
            'item_en': ['Total Assets', 'Total Liabilities', 'Total Equity'],
            'item_id': ['total_assets', 'total_liabilities', 'total_equity'],
            '2024-Q1': [5000000, 2000000, 3000000],
            '2024-Q2': [5500000, 2200000, 3300000],
        }
    }


@pytest.fixture
def mock_quote_data():
    """Mock quote/price data."""
    return {
        'time': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'open': [100.0, 102.0, 101.0],
        'high': [105.0, 108.0, 106.0],
        'low': [98.0, 101.0, 100.0],
        'close': [103.0, 107.0, 104.0],
        'volume': [1000000, 1200000, 1100000],
    }


@pytest.fixture
def mock_listing_data():
    """Mock listing data."""
    return {
        'symbol': ['VCB', 'ACB', 'TCB', 'BID', 'VNM'],
        'name': ['Vietcombank', 'ACB Bank', 'Techcombank', 'BIDV', 'Vinamilk'],
        'exchange': ['HOSE', 'HOSE', 'HOSE', 'HOSE', 'HOSE'],
        'type': ['STOCK', 'STOCK', 'STOCK', 'STOCK', 'STOCK'],
    }


# ============================================================================
# Parametrized Test Fixtures
# ============================================================================

@pytest.fixture(params=['VCI', 'TCBS', 'KBS'])
def data_source(request):
    """Parametrized fixture for testing multiple data sources."""
    return request.param


@pytest.fixture(params=['year', 'quarter'])
def report_period(request):
    """Parametrized fixture for testing different report periods."""
    return request.param


@pytest.fixture(params=['vi', 'en', None])
def language_mode(request):
    """Parametrized fixture for testing different language modes."""
    return request.param


# ============================================================================
# Cleanup and Fixture Utilities
# ============================================================================

@pytest.fixture
def temp_test_dir(tmp_path):
    """Provide temporary directory for test files."""
    return tmp_path


@pytest.fixture
def cleanup_after_test(tmp_path):
    """Fixture to cleanup test artifacts."""
    yield tmp_path
    
    # Cleanup logic
    import shutil
    if tmp_path.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)
