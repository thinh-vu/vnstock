"""
Constants and configuration cho XNO data source.
Chỉ sử dụng 2 API endpoints riêng của XNO.
Following vnstock coding standards.
"""

# XNO API Configuration - CHỈ SỬ DỤNG 2 ENDPOINTS NÀY
_XNO_API_BASE = "https://api-v2.xno.vn"
_XNO_LAMBDA_BASE = "https://lambda.xno.vn"
_DEFAULT_TIMEOUT = 30

# API Endpoints - CHỈ CÁC ENDPOINT RIÊNG CỦA XNO
_ENDPOINTS = {
    # Stock historical data từ API v2
    # Format: /quant-data/v1/stocks/{symbol}/ohlcv/{resolution}
    'stocks_ohlcv': '/quant-data/v1/stocks',
    
    # Chart data từ Lambda
    'chart': 'chart/OHLCChart/gap-chart',
}

# Timeframe mapping cho stocks_hist
_TIMEFRAME_MAP = {
    'm': 'minute',
    'h': 'hour',
    'd': 'day',
    'w': 'week',
    'M': 'month'
}

# OHLCV Column Mapping (XNO -> vnstock standard)
_OHLC_RENAME = {
    "t": "time",
    "o": "open",
    "h": "high",
    "l": "low",
    "c": "close",
    "v": "volume"
}

# Date columns cần convert sang datetime
_DATE_COLUMNS = ['date', 'time', 'trading_date']

# Supported timeframes cho history
_SUPPORTED_TIMEFRAMES = ['m', 'h', 'd', 'w', 'M']

# Request delay (seconds) để tránh rate limit
_REQUEST_DELAY = 0.1
