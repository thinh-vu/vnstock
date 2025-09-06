"""
Test script for Quote API with new parameter names.
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add parent directory to path to import vnstock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vnstock import Quote
from vnstock.core.constants import TimeResolutions

def test_quote_api():
    """Test the Quote API with different parameter combinations."""
    print("Testing Quote API with new parameter names...")
    
    # Initialize Quote object
    quote = Quote(symbol="VCI", source="vci")
    print(f"Quote object initialized with symbol=VCI, source=vci")
    
    # Test 1: Basic history with start and end
    print("\nTest 1: Basic history with start and end")
    try:
        df = quote.history(start="2024-01-01", end="2024-04-18")
        print(f"Success! Returned DataFrame shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"First few rows:\n{df.head(3)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test 2: History with different symbol
    print("\nTest 2: History with different symbol")
    try:
        df = quote.history(symbol="FPT", start="2024-01-01", end="2024-04-18")
        print(f"Success! Returned DataFrame shape: {df.shape}")
        print(f"First few rows:\n{df.head(3)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test 3: History with weekly interval
    print("\nTest 3: History with weekly interval")
    try:
        df = quote.history(start="2024-01-01", end="2024-04-18", interval=TimeResolutions.WEEKLY)
        print(f"Success! Returned DataFrame shape: {df.shape}")
        print(f"First few rows:\n{df.head(3)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test 4: History with minute interval (if supported by provider)
    print("\nTest 4: History with minute interval")
    try:
        # Sử dụng ngày cụ thể thay vì ngày hiện tại để tránh lỗi
        # VCI provider chỉ hỗ trợ định dạng ngày YYYY-MM-DD
        test_date = "2024-04-18"
        
        # Thử với cách khác để lấy dữ liệu theo phút
        df = quote.history(start=test_date, end=test_date, interval=TimeResolutions.MINUTE_5)
        print(f"Success! Returned DataFrame shape: {df.shape}")
        print(f"First few rows:\n{df.head(3)}")
    except Exception as e:
        print(f"Error: {str(e)}")
        # In thêm thông tin chi tiết về lỗi
        import traceback
        print(f"Detailed error: {traceback.format_exc()}")
    
    # Test 5: Intraday data
    print("\nTest 5: Intraday data")
    try:
        df = quote.intraday()
        print(f"Success! Returned DataFrame shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"First few rows:\n{df.head(3)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test 6: Price depth
    print("\nTest 6: Price depth")
    try:
        df = quote.price_depth()
        print(f"Success! Returned DataFrame shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"First few rows:\n{df.head(3)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_quote_api()
