_BASE_URL = 'https://apipubaws.tcbs.com.vn'
_STOCKS_URL = 'stock-insight'
_FUTURE_URL = 'futures-insight'
_ANALYSIS_URL = 'tcanalysis'

_INTERVAL_MAP = {'1m' : '1',
            '5m' : '5',
            '15m' : '15',
            '30m' : '30',
            '1H' : '60',
            '1D' : 'D',
            '1W' : 'W',
            '1M' : 'M'
            }
        

_OHLC_MAP = {
    'tradingDate': 'time',
    'open': 'open',
    'high': 'high',
    'low': 'low',
    'close': 'close',
    'volume': 'volume',
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

_INTRADAY_MAP = {
            "t": "time",
            "p": 'price',
            "v": 'volume',
            "a": "match_type",
        }

_INTRADAY_DTYPE = {
                    "price": "float64",
                    "volume": "int64",
                    "time": "datetime64[ns]",
                    "match_type": "category"
                }

_PRICE_BOARD_EXT_COLS = ['t', 'cp', 'fv', 'mav', 'nstv', 'nstp', 'rsi', 'macdv', 'macdsignal',
        'tsignal', 'avgsignal', 'ma20', 'ma50', 'ma100', 'session', 'mw3d',
        'mw1m', 'mw3m', 'mw1y', 'rs3d', 'rs1m', 'rs3m', 'rs1y', 'rsavg', 'hp1m',
        'hp3m', 'hp1y', 'lp1m', 'lp3m', 'lp1y', 'hp1yp', 'lp1yp', 'pe', 'pb',
        'roe', 'oscore', 'av', 'bv', 'ev', 'hmp', 'mscore', 'delta1m',
        'delta1y', 'vnipe', 'vnipb', 'vnid3d', 'vnid1m', 'vnid3m', 'vnid1y']

_PRICE_BOARD_STD_COLS = ['t', 'cp', 'nstv', 'nstp', 'session', 'mw3d',
        'mw1m', 'mw3m', 'mw1y', 'hp1m',
        'hp3m', 'hp1y', 'lp1m', 'lp3m', 'lp1y', 'hp1yp', 'lp1yp', 'pe', 'pb',
        'roe', 'oscore', 'av', 'bv', 'ev', 'hmp', 'mscore', 'delta1m',
        'delta1y']

_PRICE_BOARD_COLS_MAP = {
                    't' : 'Mã CP', 'cp' : 'Giá', 
                    'fv' : 'KLBD/TB5D', 'mav' : 'T.độ GD', 
                    'nstv' : 'KLGD ròng(CM)', 'nstp' : '%KLGD ròng (CM)', 
                    'rsi' : 'RSI', 'macdv' : 'MACD Hist', 'macdsignal' : 'MACD Signal', 
                    'tsignal' : 'Tín hiệu KT', 'avgsignal' : 'Tín hiệu TB động', 
                    'ma20' : 'MA20', 'ma50' : 'MA50', 'ma100' : 'MA100', 
                    'session' : 'Phiên +/- ', 'mscore' : 'Đ.góp VNINDEX', 
                    'pe' : 'P/E', 'pb' : 'P/B', 'roe' : 'ROE', 'oscore' : 'TCRating', 
                    'ev' : 'TCBS định giá', 'mw3d' : '% thay đổi giá 3D', 'mw1m' : '% thay đổi giá 1M', 
                    'mw3m' : '% thay đổi giá 3M', 'mw1y' : '% thay đổi giá 1Y', 
                    'rs3d' : 'RS 3D', 'rs1m' : 'RS 1M', 'rs3m' : 'RS 3M', 
                    'rs1y' : 'RS 1Y', 'rsavg' : 'RS TB', 'hp1m' : 'Đỉnh 1M', 
                    'hp3m' : 'Đỉnh 3M', 'hp1y' : 'Đỉnh 1Y', 'lp1m' : 'Đáy 1M', 
                    'lp3m' : 'Đáy 3M', 'lp1y' : 'Đáy 1Y', 'hp1yp' : '%Đỉnh 1Y', 
                    'lp1yp' : '%Đáy 1Y', 'delta1m' : '%Giá - %VNI (1M)', 'delta1y' : '%Giá - %VNI (1Y)', 
                    'bv' : 'Khối lượng Dư mua', 'av' : 'Khối lượng Dư bán', 'hmp' : 'Khớp nhiều nhất', 'vnipe':'VNINDEX P/E', 'vnipb':'VNINDEX P/B'
                    }

_FINANCIAL_REPORT_MAP = {'balance_sheet': 'balancesheet', 
                            'income_statement': 'incomestatement', 
                            'cash_flow': 'cashflow'}

_FINANCIAL_REPORT_PERIOD_MAP = {'year': 1, 'quarter': 0}