"""Constants for DNSE (Entrade) data source."""

# Base URL
_BASE_URL = "https://services.entrade.com.vn"

# OHLCV history endpoint
_OHLC_URL = f"{_BASE_URL}/chart-api/v2/ohlcs/stock"

# Intraday tick endpoint
_INTRADAY_URL = f"{_BASE_URL}/dnse-order-api/v2/user/transaction-buy-sell-history"

# Price board (multi-symbol snapshot) endpoint
_PRICE_BOARD_URL = f"{_BASE_URL}/chart-api/v2/quotes"

# Interval map: user-friendly key → DNSE API resolution string
_INTERVAL_MAP = {
    # Minute intervals
    "1m": "1",
    "5m": "5",
    "15m": "15",
    "30m": "30",
    # Hour intervals
    "1H": "60",
    "1h": "60",
    "60m": "60",
    # Daily
    "1D": "D",
    "1d": "D",
    "D": "D",
    "d": "D",
    "daily": "D",
    # Weekly
    "1W": "W",
    "1w": "W",
    "W": "W",
    "w": "W",
    "weekly": "W",
    # Monthly
    "1M": "M",
    "M": "M",
    "monthly": "M",
}

# Column mapping for OHLCV response
# DNSE API returns: t, o, h, l, c, v (similar to KBS)
_OHLC_MAP = {
    "t": "time",
    "o": "open",
    "h": "high",
    "l": "low",
    "c": "close",
    "v": "volume",
}

# Data type mapping for OHLCV data
_OHLC_DTYPE = {
    "time": "datetime64[ns]",
    "open": "float64",
    "high": "float64",
    "low": "float64",
    "close": "float64",
    "volume": "int64",
}

# Column mapping for intraday tick response
# DNSE returns transaction buy/sell history per day
_INTRADAY_MAP = {
    "time": "time",
    "price": "price",
    "volume": "volume",
    "side": "match_type",  # 'B' or 'S' from API
    "id": "id",
    # fallback raw key names from DNSE API
    "t": "time",
    "p": "price",
    "v": "volume",
    "a": "match_type",
    "seq": "id",
}

# Data type mapping for intraday data
_INTRADAY_DTYPE = {
    "time": "object",
    "price": "float64",
    "volume": "int64",
    "match_type": "object",
    "id": "object",
}

# Standard intraday output columns (matches KBS/VCI schema)
_INTRADAY_CORE_COLUMNS = ["time", "price", "volume", "match_type", "id"]

# Column mapping for price board response
# DNSE /chart-api/v2/quotes returns a symbol object per entry
_PRICE_BOARD_MAP = {
    "sym": "symbol",
    "symbol": "symbol",
    "c": "close_price",  # last match / current price
    "f": "floor_price",
    "ce": "ceiling_price",
    "r": "reference_price",
    "o": "open_price",
    "h": "high_price",
    "l": "low_price",
    "lastPrice": "close_price",
    "lastVolume": "volume_last",
    "totalVolume": "volume_accumulated",
    "totalValue": "total_value",
    "change": "price_change",
    "changePercent": "percent_change",
    "pcp": "percent_change",
    "lot": "volume_last",
    "ot": "time",
    "t": "time",
    # Bid/Ask
    "b1": "bid_price_1",
    "bv1": "bid_vol_1",
    "b2": "bid_price_2",
    "bv2": "bid_vol_2",
    "b3": "bid_price_3",
    "bv3": "bid_vol_3",
    "s1": "ask_price_1",
    "sv1": "ask_vol_1",
    "s2": "ask_price_2",
    "sv2": "ask_vol_2",
    "s3": "ask_price_3",
    "sv3": "ask_vol_3",
    # Foreign flow
    "fBuyVol": "foreign_buy_volume",
    "fSellVol": "foreign_sell_volume",
    "fRoom": "foreign_room",
}

# Standard columns for price board output (matches KBS schema subset)
_PRICE_BOARD_STANDARD_COLUMNS = [
    "symbol",
    "time",
    "ceiling_price",
    "floor_price",
    "reference_price",
    "open_price",
    "high_price",
    "low_price",
    "close_price",
    "volume_last",
    "volume_accumulated",
    "total_value",
    "price_change",
    "percent_change",
    "bid_price_1",
    "bid_vol_1",
    "bid_price_2",
    "bid_vol_2",
    "bid_price_3",
    "bid_vol_3",
    "ask_price_1",
    "ask_vol_1",
    "ask_price_2",
    "ask_vol_2",
    "ask_price_3",
    "ask_vol_3",
    "foreign_buy_volume",
    "foreign_sell_volume",
    "foreign_room",
]
