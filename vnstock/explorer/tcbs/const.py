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

_INDEX_MAPPING = {'VNINDEX': 'VNINDEX', 'HNXINDEX': 'HNXIndex', 'UPCOMINDEX': 'UPCOM'}

_SCREENER_MAPPING = {
    "exchange_name": "exchange",
    "industry_name": "industry",
    "company_name": "company_name",
    "roe": "roe",
    "active_buy_percentage": "active_buy_pct",
    "strong_buy_percentage": "strong_buy_pct",
    "suddenly_high_volume_matching": "high_vol_match",
    "forecast_volume_ratio": "forecast_vol_ratio",
    "ev_ebitda": "ev_ebitda",
    "revenue_growth1_year": "revenue_growth_1y",
    "revenue_growth5_year": "revenue_growth_5y",
    "eps_growth1_year": "eps_growth_1y",
    "eps_growth5_year": "eps_growth_5y",
    "avg_trading_value5_day": "avg_trading_value_5d",
    "avg_trading_value10_day": "avg_trading_value_10d",
    "avg_trading_value20_day": "avg_trading_value_20d",
    "relative_strength3_day": "relative_strength_3d",
    "relative_strength1_month": "rel_strength_1m",
    "relative_strength3_month": "rel_strength_3m",
    "relative_strength1_year": "rel_strength_1y",
    "foreign_volume_percent": "foreign_vol_pct",
    "foreign_buy_sell20_session": "foreign_buysell_20s",
    "volume_vs_v_sma5": "vol_vs_sma5",
    "volume_vs_v_sma10": "vol_vs_sma10",
    "volume_vs_v_sma20": "vol_vs_sma20",
    "volume_vs_v_sma50": "vol_vs_sma50",
    "price_growth1_week": "price_growth_1w",
    "price_growth1_month": "price_growth_1m",
    "prev1_day_growth_percent": "prev_1d_growth_pct",
    "prev1_month_growth_percent": "prev_1m_growth_pct",
    "prev1_year_growth_percent": "prev_1y_growth_pct",
    "prev5_year_growth_percent": "prev_5y_growth_pct",
    "profit_for_the_last4_quarters": "profit_last_4q",
    "percent1_year_from_peak": "pct_1y_from_peak",
    "percent_away_from_historical_peak": "pct_away_from_hist_peak",
    "percent1_year_from_bottom": "pct_1y_from_bottom",
    "percent_off_historical_bottom": "pct_off_hist_bottom",
}
