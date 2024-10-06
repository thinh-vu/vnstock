_BASE_URL = 'https://assets.msn.com/service/Finance'

_SYMBOL_INDEX_COLS_MAP = {
                        'RT00S': 'symbol',
                        'SecId': 'symbol_id',
                        'AC040': 'exchange_name',
                        'LS01Z': 'exchange_code_mic',
                        'AC042': 'short_name',
                        'FriendlyName': 'friendly_name',
                        'RT0SN': 'eng_name',
                        'Description': 'description',
                        'OS0LN': 'local_name',
                        'locale': 'locale'
                        }

_INTERVAL_MAP = {
                '1D': '1D',
                '1M':'Max'
                }

_RESAMPLE_MAP = {
    '1D': '1D',
    '1W': '1W',
    '1M': 'ME'
}

_OHLC_MAP = {
    'timeStamps': 'time',
    'openPrices': 'open',
    'pricesHigh': 'high',
    'pricesLow': 'low',
    'prices': 'close',
    'volumes': 'volume',
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

_CURRENCY_ID_MAP = {
                    'USDVND': 'avyufr',
                    'JPYVND': 'ave8sm',
                    'AUDVND': 'auxrkr',
                    'CNYVND': 'av55fr',
                    'KRWVND': 'avfg9c',
                    'USDJPY': 'avyomw',
                    'USDEUR': 'avyn9c',
                    'USDCAD': 'avylur',
                    'USDCHF': 'avyt7w',
                    'USDCNY': 'avym77',
                    'USDKRW': 'avyoyc',
                    'USDSGD': 'avyspr',
                    'USDHKD': 'avynz2',
                    'USDTRY': 'avytp2',
                    'USDINR': 'avyo8m',
                    'USDDKK': 'avymr7',
                    'USDSEK': 'avyt52',
                    'USDILS': 'avyoh7',
                    'USDRUB': 'avys2w',
                    'USDMXN': 'avyqcw',
                    'USDZAR': 'avysvh',
                    'EURUSD': 'av932w',
                    'EURVND': 'av93ec',
                    'EURJPY': 'av8wim',
                    'EURGBP': 'av92z2',
                    'EURCHF': 'av923m',
                    'EURCAD': 'av8ttc',
                    'EURAUD': 'av8sfr',
                    'EURNZD': 'av8ysm',
                    'GBPJPY': 'avye1h',
                    'GBPVND': 'avyjtc',
                    'GBPUSD': 'avyjhw',
                    'GBPAUD': 'avy9ur',
                    'GBPCHF': 'avyilh',
                    'GBPNZD': 'avygbh',
                    'GBPCAD': 'avyb9c',
                    'AUDUSD': 'auxr9c',
                    'NZDUSD': 'avmpm7',
                    }

_CRYPTO_ID_MAP = {
                    'BTC': 'c2111',
                    'ETH': 'c2112',
                    'USDT': 'c2115',
                    'USDC': 'c211a', 
                    'BNB': 'c2113',
                    'BUSD': 'c211i',
                    'XRP': 'c2117',
                    'ADA': 'c2114',
                    'SOL': 'c2116',
                    'DOGE': 'c2119'
                    }


_GLOBAL_INDICES = {
                    'INX': 'a33k6h', # S&P 500 Index
                    'DJI': 'a6qja2', # Dow Jones Industrial Average
                    'COMP': 'a3oxnm', # Nasdaq Composite Index
                    'RUT': 'b9v42w', # Russell 2000 Index
                    'NYA': 'a74pqh', # NYSE Composite Index
                    'RUI': 'a33fcw', # Russell 1000 Index
                    'RUA': 'bggnm7', # Russell 3000 Index
                    'UKX': 'aopnp2', # FTSE 100 Index
                    'DAX': 'afx2kr', # DAX Index
                    'PX1': 'aecfh7', # CAC 40 Index
                    'N225': 'a9j7bh', # Nikkei 225 Index
                    '000001': 'adfh77', # Shanghai SE Composite Index
                    'HSI': 'ah7etc', # Hang Seng Index
                    'SENSEX': 'ahkucw', # S&P BSE Sensex Index
                    'ME00000000': 'ale3jc', # S&P/BMV IPC
                    'VNI': 'aqk2nm' # VN Index
                    }