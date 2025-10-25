"""
Constants and configuration for FMP connector.
Following VCI patterns for consistency.
"""

# FMP API Configuration
_FMP_DOMAIN = "https://financialmodelingprep.com/stable"
_API_V3 = '/api/v3'
_API_V4 = '/api/v4'

# Default configurations
_DEFAULT_TIMEOUT = 30
_DEFAULT_API_KEY = 'demo'

# Endpoint mappings for FMP API (based on current FMP structure)
# FMP API Endpoints (sử dụng /stable domain)
# ✅ = Đã test hoạt động | ❌ = Endpoint không khả dụng với gói hiện tại
_ENDPOINTS = {
    # Quote & Price Data
    'quote': '/quote',  # ✅ Tested
    'quote_short': '/quote-short',  # ✅ Tested
    # Historical price endpoints (end-of-day)
    'historical_price_eod': '/historical-price-eod',  # ✅ Available
    # Note: historical-chart endpoints cần subscription cao hơn
    'historical_chart_1min': '/historical-chart/1min',  # ✅ Tested
    'historical_chart_5min': '/historical-chart/5min',  # ✅ Tested
    'historical_chart_15min': '/historical-chart/15min',  # ✅ Tested
    'historical_chart_30min': '/historical-chart/30min',  # ✅ Tested
    'historical_chart_1hour': '/historical-chart/1hour',  # ✅ Tested
    'historical_chart_4hour': '/historical-chart/4hour',  # ✅ Tested

    # Company Information
    'profile': '/profile',  # ✅ Tested
    'key_executives': '/key-executives',  # ✅ Tested
    'stock_news': '/stock-latest',  # ❌ 404
    'stock_calendar_events': '/stock-dividend-calendar',

    # Financial Statements
    'income_statement': '/income-statement',  # ✅ Tested
    'balance_sheet': '/balance-sheet-statement',  # ✅ Tested
    'cashflow_statement': '/cash-flow-statement',
    'ratios': '/ratios',  # ✅ Tested
    'financial_growth': '/financial-growth',
    'key_metrics': '/key-metrics',
    'financial_score': '/score',

    # Market Data
    'search': '/search',
    'search_ticker': '/search-ticker',
    'search_symbol': '/search-symbol',  # ✅ Tested
    'available_traded': '/available-traded/list',  # ❌ 404
    'stock_list': '/stock/list',  # ❌ 404
    'etf_list': '/etf/list',  # ❌ 404

    # Analyst & Rating
    'analyst_estimates': '/analyst-estimates',
    'rating': '/rating',  # ❌ 404
    'historical_rating': '/historical-rating',

    # Dividends & Splits
    'historical_dividends': '/historical-price-full/stock-dividend',
    'stock_split': '/historical-price-full/stock-split',
}

# Date columns cần convert sang datetime
_DATE_COLUMNS = [
    'date', 'filingDate', 'acceptedDate', 'publishedDate',
    'paymentDate', 'recordDate', 'declarationDate',
    'calendarYear', 'period', 'ipoDate'
]

# Numeric columns cần convert sang numeric type
_NUMERIC_COLUMNS = [
    'price', 'change', 'changePercentage', 'volume',
    'marketCap', 'beta', 'revenue', 'netIncome',
    'eps', 'epsDiluted', 'pe', 'priceToBook'
]

# Supported intervals for historical data
_SUPPORTED_INTERVALS = [
    '1min', '5min', '15min', '30min', '1hour', '4hour', '1day'
]

# Period mapping
_PERIOD_MAP = {
    'annual': 'annual',
    'quarter': 'quarter',
    'yearly': 'annual',
    'quarterly': 'quarter'
}

# Exchange mappings
_EXCHANGE_MAP = {
    'NYSE': 'New York Stock Exchange',
    'NASDAQ': 'NASDAQ',
    'AMEX': 'American Stock Exchange',
    'LSE': 'London Stock Exchange',
    'TSE': 'Tokyo Stock Exchange'
}

# Column mappings for standardization (following VCI patterns)
_OHLCV_MAP = {
    'date': 'time',
    'open': 'open',
    'high': 'high',
    'low': 'low',
    'close': 'close',
    'volume': 'volume'
}

# Data type mapping for DataFrame
_OHLCV_DTYPE = {
    'time': 'datetime64[ns]',
    'open': 'float64',
    'high': 'float64',
    'low': 'float64',
    'close': 'float64',
    'volume': 'int64'
}
