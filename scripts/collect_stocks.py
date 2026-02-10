"""
Thu thập dữ liệu OHLCV lịch sử cho top 500 cổ phiếu vốn hóa lớn nhất.

Nguồn: VNDirect dchart API (TradingView UDF format) - full OHLCV, không cần auth.
Cache: SQLite (data/cache.db) - lần đầu fetch full, hàng ngày chỉ fetch ngày mới.

Output:
    data/stocks/
    ├── VCB.csv
    ├── FPT.csv
    ├── VNM.csv
    └── ... (500 files)

Cách chạy:
    python scripts/collect_stocks.py                        # Hàng ngày: fetch phiên mới nhất
    python scripts/collect_stocks.py --start 2025-01-01     # Backfill từ ngày cụ thể
    python scripts/collect_stocks.py --top-n 100            # Chỉ lấy top 100 vốn hóa
"""

import sys
import time
import logging
import argparse
import requests
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd

# ============================================================
# CẤU HÌNH
# ============================================================

DATA_DIR = PROJECT_ROOT / "data" / "stocks"

# VNDirect dchart API
_VND_CHART_URL = "https://dchart-api.vndirect.com.vn/dchart/history"
_VND_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://dchart.vndirect.com.vn",
    "Origin": "https://dchart.vndirect.com.vn",
}

REQUEST_DELAY = 0.15  # ~7 req/s (Golden Sponsor: 500 req/min)
BATCH_SIZE = 50       # Log progress mỗi 50 mã

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("stocks")


# ============================================================
# LẤY TOP 500 VỐN HÓA
# ============================================================

def get_top_symbols(top_n: int = 500) -> list:
    """
    Lấy top N mã cổ phiếu vốn hóa lớn nhất từ KBS price_board.

    Returns:
        List of symbol strings sorted by market cap descending.
    """
    from vnstock.common.client import Vnstock

    logger.info(f"Đang lấy danh sách mã cổ phiếu...")
    client = Vnstock(source="VCI", show_log=False)
    stock = client.stock(symbol="ACB", source="VCI")
    symbols_df = stock.listing.symbols_by_exchange(show_log=False)
    all_symbols = symbols_df["symbol"].tolist()
    logger.info(f"Tổng: {len(all_symbols)} mã")

    # Fetch KBS board để xác định vốn hóa
    logger.info(f"Đang lấy bảng giá KBS để xếp hạng vốn hóa...")
    client_kbs = Vnstock(source="KBS", show_log=False)
    stock_kbs = client_kbs.stock(symbol="ACB", source="KBS")

    all_data = []
    batch_size = 50
    total = len(all_symbols)
    for i in range(0, total, batch_size):
        batch = all_symbols[i:i + batch_size]
        try:
            df = stock_kbs.trading.price_board(symbols_list=batch, get_all=True)
            if df is not None and not df.empty:
                all_data.append(df)
        except Exception as e:
            logger.warning(f"  KBS batch lỗi: {e}")
        if i + batch_size < total:
            time.sleep(0.5)

    if not all_data:
        logger.error("Không lấy được bảng giá KBS.")
        return all_symbols[:top_n]

    board = pd.concat(all_data, ignore_index=True)

    # Tính market cap
    for col in ['close_price', 'listed_shares', 'total_listed_qty']:
        if col in board.columns:
            board[col] = pd.to_numeric(board[col], errors='coerce')

    shares_col = 'total_listed_qty' if 'total_listed_qty' in board.columns else 'listed_shares'
    if shares_col in board.columns and 'close_price' in board.columns:
        board['market_cap'] = board['close_price'] * board[shares_col]
    else:
        board['market_cap'] = 0

    board = board.dropna(subset=['market_cap'])
    board = board[board['market_cap'] > 0]
    top = board.nlargest(top_n, 'market_cap')

    symbols = top['symbol'].tolist()
    logger.info(f"Top {top_n} vốn hóa: {len(symbols)} mã ({symbols[0]}...{symbols[-1]})")
    return symbols


# ============================================================
# FETCH OHLCV TỪ VNDIRECT
# ============================================================

def fetch_stock_ohlcv(symbol: str, start: str, end: str) -> pd.DataFrame:
    """
    Lấy OHLCV lịch sử cho 1 mã cổ phiếu từ VNDirect dchart API.
    """
    start_ts = int(datetime.strptime(start, "%Y-%m-%d").timestamp())
    end_ts = int((datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1)).timestamp())

    params = {
        "resolution": "D",
        "symbol": symbol,
        "from": start_ts,
        "to": end_ts,
    }

    try:
        resp = requests.get(
            _VND_CHART_URL, params=params, headers=_VND_HEADERS, timeout=30
        )
        if resp.status_code != 200:
            return pd.DataFrame()

        if not resp.text or not resp.text.strip():
            return pd.DataFrame()

        data = resp.json()
        if data.get("s") != "ok":
            return pd.DataFrame()

        times = data.get("t", [])
        if not times:
            return pd.DataFrame()

        df = pd.DataFrame({
            "time": pd.to_datetime(times, unit="s"),
            "open": pd.to_numeric(data.get("o", []), errors="coerce"),
            "high": pd.to_numeric(data.get("h", []), errors="coerce"),
            "low": pd.to_numeric(data.get("l", []), errors="coerce"),
            "close": pd.to_numeric(data.get("c", []), errors="coerce"),
            "volume": np.nan_to_num(
                pd.to_numeric(data.get("v", []), errors="coerce"), nan=0
            ).astype("int64"),
        })

        df = df[(df["time"] >= start) & (df["time"] <= end)]
        df = df.sort_values("time").reset_index(drop=True)
        return df

    except Exception as e:
        logger.debug(f"  {symbol}: lỗi - {e}")
        return pd.DataFrame()


def fetch_stock_with_cache(symbol: str, start: str, end: str) -> pd.DataFrame:
    """
    Fetch OHLCV cho 1 mã, sử dụng SQLite cache.
    Chỉ gọi API cho ngày chưa có trong cache.
    """
    from db_cache import (
        get_cached_stock, save_stock_data, compute_fetch_range
    )

    fetch_start, fetch_end = compute_fetch_range(
        symbol, start, end, table="stock_ohlcv", fresh_days=3
    )

    if fetch_start is None:
        # Cache đầy đủ
        df = get_cached_stock(symbol, start, end)
        return df

    # Fetch dữ liệu mới
    new_data = fetch_stock_ohlcv(symbol, fetch_start, fetch_end)

    if new_data is not None and not new_data.empty:
        save_stock_data(symbol, new_data)

    # Đọc lại từ cache (merged)
    df = get_cached_stock(symbol, start, end)
    return df


# ============================================================
# CHỈ BÁO KỸ THUẬT
# ============================================================

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Thêm các chỉ báo kỹ thuật: SMA, RSI, MACD, Bollinger Bands."""
    df = df.copy()
    close = df["close"]

    # Moving Averages
    for p in [20, 50, 200]:
        df[f"sma_{p}"] = close.rolling(window=p, min_periods=1).mean()

    # RSI 14
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14).mean()
    rs = avg_gain / avg_loss
    df["rsi_14"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    # Bollinger Bands
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    df["bb_upper"] = sma20 + 2 * std20
    df["bb_lower"] = sma20 - 2 * std20

    # Biến động
    df["daily_return"] = close.pct_change() * 100
    df["volatility_20d"] = df["daily_return"].rolling(20).std()

    return df


# ============================================================
# MAIN COLLECTOR
# ============================================================

def collect_stocks(symbols: list, start: str, end: str):
    """
    Thu thập OHLCV cho danh sách mã cổ phiếu.
    Lưu mỗi mã thành 1 file CSV riêng.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    total = len(symbols)
    success = 0
    cached = 0
    api_calls = 0
    errors = []

    for idx, symbol in enumerate(symbols):
        if (idx + 1) % BATCH_SIZE == 0 or idx == 0:
            logger.info(f"  [{idx + 1}/{total}] {symbol}... (OK: {success}, cache: {cached}, API: {api_calls})")

        from db_cache import get_last_cached_date
        had_cache = get_last_cached_date(symbol, "stock_ohlcv") is not None

        try:
            df = fetch_stock_with_cache(symbol, start, end)

            if df is not None and not df.empty:
                # Tính chỉ báo kỹ thuật
                df = add_indicators(df)
                df["symbol"] = symbol
                csv_path = DATA_DIR / f"{symbol}.csv"
                df.to_csv(csv_path, index=False, encoding="utf-8-sig")
                success += 1

                if had_cache:
                    cached += 1
                else:
                    api_calls += 1
            else:
                errors.append(symbol)
        except Exception as e:
            errors.append(symbol)
            logger.debug(f"  {symbol}: lỗi - {e}")

        # Rate limiting
        time.sleep(REQUEST_DELAY)

    logger.info(f"\nKết quả: {success}/{total} mã thành công")
    logger.info(f"  Cache hit: {cached} | API fetch: {api_calls} | Lỗi: {len(errors)}")
    if errors:
        logger.warning(f"  Mã lỗi: {errors[:20]}{'...' if len(errors) > 20 else ''}")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Thu thập OHLCV lịch sử cho top N cổ phiếu vốn hóa lớn nhất.",
    )
    parser.add_argument("--start", default=None,
                        help="Ngày bắt đầu (YYYY-MM-DD). Mặc định: 1 năm trước")
    parser.add_argument("--end", default=None,
                        help="Ngày kết thúc (YYYY-MM-DD). Mặc định: hôm nay")
    parser.add_argument("--top-n", type=int, default=500,
                        help="Số mã vốn hóa lớn nhất (mặc định: 500)")
    args = parser.parse_args()

    end = args.end or datetime.now().strftime("%Y-%m-%d")
    start = args.start or (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    # Cache stats
    from db_cache import get_cache_stats
    stats = get_cache_stats()
    stock_stats = stats.get("stock_ohlcv", {})

    logger.info("=" * 60)
    logger.info("THU THẬP OHLCV CỔ PHIẾU")
    logger.info(f"Thời gian: {start} -> {end}")
    logger.info(f"Top: {args.top_n} vốn hóa lớn nhất")
    logger.info(f"Nguồn: VNDirect dchart API + SQLite cache")
    logger.info(f"Cache: {stock_stats.get('rows', 0)} rows, {stock_stats.get('symbols', 0)} symbols")
    logger.info(f"Output: {DATA_DIR}")
    logger.info("=" * 60)

    # 1. Lấy danh sách top N
    logger.info("\n[1/2] XÁC ĐỊNH TOP MÃ VỐN HÓA")
    symbols = get_top_symbols(top_n=args.top_n)

    if not symbols:
        logger.error("Không lấy được danh sách mã. Dừng lại.")
        return

    # 2. Fetch OHLCV
    logger.info(f"\n[2/2] FETCH OHLCV ({len(symbols)} mã)")
    collect_stocks(symbols, start, end)

    logger.info("\n" + "=" * 60)
    logger.info("HOÀN TẤT!")
    logger.info(f"Dữ liệu: {DATA_DIR}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
