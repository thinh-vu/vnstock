_BASE_URL = 'https://mt.vietcap.com.vn/api/'
_CHART_URL = 'chart/OHLCChart/gap'
_INTRADAY_URL = 'market-watch'
_GRAPHQL_URL = 'https://api.vietcap.com.vn/data-mt/graphql'

_INTERVAL_MAP = {'1m' : 'ONE_MINUTE',
            '5m' : 'ONE_MINUTE',
            '15m' : 'ONE_MINUTE',
            '30m' : 'ONE_MINUTE',
            '1H' : 'ONE_HOUR',
            '1D' : 'ONE_DAY',
            '1W' : 'ONE_DAY',
            '1M' : 'ONE_DAY'
            }
        
_RESAMPLE_MAP = {
            '5m' : '5min',
            '15m' : '15min',
            '30m' : '30min',
            '1W' : '1W',
            '1M' : 'ME'
            }

_OHLC_MAP = {
    't': 'time',
    'o': 'open',
    'h': 'high',
    'l': 'low',
    'c': 'close',
    'v': 'volume',
} 


# Pandas data type mapping for history price data
_OHLC_DTYPE = {
    "time": "datetime64[ns]",  # Convert timestamps to datetime
    "open": "float64",
    "high": "float64",
    "low": "float64",
    "close": "float64",
    "volume": "int64",
}

_GROUP_CODE = ['HOSE', 'VN30', 'VNMidCap', 'VNSmallCap', 'VNAllShare', 'VN100', 'ETF', 'HNX', 'HNX30', 'HNXCon', 'HNXFin', 'HNXLCap', 'HNXMSCap', 'HNXMan', 'UPCOM', 'FU_INDEX', 'FU_BOND', 'BOND', 'CW']

_INTRADAY_MAP = {
                'truncTime':'time',                
                'matchPrice':'price', 
                'matchVol':'volume', 
                'matchType':'match_type',
                'id':'id'
                }

_INTRADAY_DTYPE = {
                    "time": "datetime64[ns]",
                    "price": "float64",
                    "volume": "int64",
                    "match_type": "str",
                    "id": "str"
                }

_PRICE_DEPTH_MAP = {
                    'priceStep':'price', 
                    'accumulatedVolume': 'acc_volume',
                    'accumulatedBuyVolume' : 'acc_buy_volume', 
                    'accumulatedSellVolume' : 'acc_sell_volume',
                    'accumulatedUndefinedVolume': 'acc_undefined_volume',
                    }

_FINANCIAL_REPORT_MAP = {'balance_sheet': 'balancesheet', 
                            'income_statement': 'incomestatement', 
                            'cash_flow': 'cashflow'}

_FINANCIAL_REPORT_PERIOD_MAP = {'year': 'Y', 'quarter': 'Q'}

_UNIT_MAPPING = {'BILLION':'tỷ', 'PERCENT':'%', 'INDEX':'index', 'MILLION':'triệu'}