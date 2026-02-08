"""
Module tính các chỉ số phân tích kỹ thuật (Technical Analysis) từ dữ liệu OHLCV.

Không cần thư viện bên ngoài, chỉ dùng pandas + numpy.
"""

import numpy as np
import pandas as pd


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Thêm toàn bộ chỉ số kỹ thuật phổ biến vào DataFrame OHLCV.

    Yêu cầu cột: close, high, low, volume (và open nếu có).
    Trả về DataFrame gốc với thêm các cột chỉ số.
    """
    df = df.copy()

    # --- Moving Averages ---
    for period in [5, 10, 20, 50, 200]:
        df[f"sma_{period}"] = sma(df["close"], period)
        df[f"ema_{period}"] = ema(df["close"], period)

    # --- RSI ---
    df["rsi_14"] = rsi(df["close"], 14)

    # --- MACD ---
    macd_line, signal, histogram = macd(df["close"])
    df["macd"] = macd_line
    df["macd_signal"] = signal
    df["macd_hist"] = histogram

    # --- Bollinger Bands ---
    upper, middle, lower = bollinger_bands(df["close"], 20, 2)
    df["bb_upper"] = upper
    df["bb_middle"] = middle
    df["bb_lower"] = lower

    # --- ATR ---
    df["atr_14"] = atr(df["high"], df["low"], df["close"], 14)

    # --- Stochastic ---
    k, d = stochastic(df["high"], df["low"], df["close"], 14, 3)
    df["stoch_k"] = k
    df["stoch_d"] = d

    # --- OBV ---
    df["obv"] = obv(df["close"], df["volume"])

    # --- Williams %R ---
    df["williams_r"] = williams_r(df["high"], df["low"], df["close"], 14)

    # --- VWAP (nếu có volume) ---
    if "volume" in df.columns:
        df["vwap"] = vwap(df["high"], df["low"], df["close"], df["volume"])

    # --- Biến động giá ---
    df["price_change"] = df["close"].diff()
    df["price_change_pct"] = df["close"].pct_change() * 100
    df["volume_change_pct"] = df["volume"].pct_change() * 100

    return df


# ============================================================
# MOVING AVERAGES
# ============================================================

def sma(series: pd.Series, period: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=period, min_periods=1).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=period, adjust=False).mean()


# ============================================================
# OSCILLATORS
# ============================================================

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal_period: int = 9):
    """MACD (Moving Average Convergence Divergence)."""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
               k_period: int = 14, d_period: int = 3):
    """Stochastic Oscillator (%K, %D)."""
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    k = 100 * (close - lowest_low) / (highest_high - lowest_low)
    d = k.rolling(window=d_period).mean()
    return k, d


def williams_r(high: pd.Series, low: pd.Series, close: pd.Series,
               period: int = 14) -> pd.Series:
    """Williams %R."""
    highest_high = high.rolling(window=period).max()
    lowest_low = low.rolling(window=period).min()
    return -100 * (highest_high - close) / (highest_high - lowest_low)


# ============================================================
# VOLATILITY
# ============================================================

def bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2):
    """Bollinger Bands (upper, middle, lower)."""
    middle = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    return upper, middle, lower


def atr(high: pd.Series, low: pd.Series, close: pd.Series,
        period: int = 14) -> pd.Series:
    """Average True Range."""
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


# ============================================================
# VOLUME
# ============================================================

def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On-Balance Volume."""
    direction = np.sign(close.diff()).fillna(0)
    return (direction * volume).cumsum()


def vwap(high: pd.Series, low: pd.Series, close: pd.Series,
         volume: pd.Series) -> pd.Series:
    """Volume Weighted Average Price."""
    typical_price = (high + low + close) / 3
    cumulative_tp_vol = (typical_price * volume).cumsum()
    cumulative_vol = volume.cumsum()
    return cumulative_tp_vol / cumulative_vol
