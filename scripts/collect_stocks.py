"""
Thu thập dữ liệu OHLCV lịch sử cho top 500 cổ phiếu vốn hóa lớn nhất.

Nguồn: VNDirect dchart API (TradingView UDF format) - full OHLCV, không cần auth.
Cache: Đọc file CSV đã commit trong repo, chỉ fetch phần mới.

Output:
    data/stocks/
    ├── VCB.csv
    ├── FPT.csv
    ├── VNM.csv
    └── ... (500 files)

Cách chạy:
    python scripts/collect_stocks.py                        # Hàng ngày: chỉ fetch phần mới
    python scripts/collect_stocks.py --start 2025-01-01     # Backfill từ ngày cụ thể
    python scripts/collect_stocks.py --top-n 100            # Chỉ lấy top 100 vốn hóa
    python scripts/collect_stocks.py --full                 # Force fetch lại toàn bộ
"""

import sys
import time
import logging
import argparse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
from utils import init_rate_limiter, get_limiter

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

REQUEST_DELAY = 0.02  # delay giữa mỗi request (chỉ dùng cho fallback)
BATCH_SIZE = 50       # Log progress mỗi 50 mã
MAX_WORKERS = 10      # Số thread song song cho VNDirect API

# Reuse HTTP session for connection pooling
_session = requests.Session()
_session.headers.update(_VND_HEADERS)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("stocks")


# ============================================================
# LẤY TOP 500 VỐN HÓA
# ============================================================

def get_top_symbols(top_n: int = 500) -> list:
    """Lấy top N mã cổ phiếu vốn hóa lớn nhất từ KBS price_board."""
    from vnstock.common.client import Vnstock

    logger.info("Đang lấy danh sách mã cổ phiếu...")
    client = Vnstock(source="VCI", show_log=False)
    stock = client.stock(symbol="ACB", source="VCI")
    symbols_df = stock.listing.symbols_by_exchange(show_log=False)
    all_symbols = symbols_df["symbol"].tolist()
    logger.info(f"Tổng: {len(all_symbols)} mã")

    logger.info("Đang lấy bảng giá KBS để xếp hạng vốn hóa...")
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
            get_limiter().wait()

    if not all_data:
        logger.error("Không lấy được bảng giá KBS.")
        return all_symbols[:top_n]

    board = pd.concat(all_data, ignore_index=True)
    logger.info(f"KBS board: {len(board)} mã")

    # Convert numeric columns
    for col in ['close_price', 'reference_price', 'listed_shares', 'total_listed_qty']:
        if col in board.columns:
            board[col] = pd.to_numeric(board[col], errors='coerce')

    # Use close_price, fallback to reference_price when close=0 (outside trading hours)
    if 'close_price' in board.columns and 'reference_price' in board.columns:
        board['price'] = board['close_price'].where(
            board['close_price'] > 0, board['reference_price']
        )
    elif 'close_price' in board.columns:
        board['price'] = board['close_price']
    elif 'reference_price' in board.columns:
        board['price'] = board['reference_price']
    else:
        logger.warning("Không có cột giá, dùng thứ tự mặc định.")
        return all_symbols[:top_n]

    shares_col = None
    for col in ['total_listed_qty', 'listed_shares']:
        if col in board.columns and board[col].sum() > 0:
            shares_col = col
            break

    if shares_col:
        board['market_cap'] = board['price'] * board[shares_col]
        logger.info(f"Market cap: price * {shares_col}")
    elif 'total_value' in board.columns:
        board['total_value'] = pd.to_numeric(board['total_value'], errors='coerce')
        board['market_cap'] = board['total_value']
        logger.info("Market cap: fallback to total_value")
    else:
        logger.warning("Không tính được market cap, dùng thứ tự mặc định.")
        return all_symbols[:top_n]

    board = board.dropna(subset=['market_cap'])
    board = board[board['market_cap'] > 0]

    if board.empty:
        logger.warning(f"Market cap = 0, dùng thứ tự mặc định (top {top_n}).")
        return all_symbols[:top_n]

    top = board.nlargest(top_n, 'market_cap')
    symbols = top['symbol'].tolist()
    logger.info(f"Top {top_n} vốn hóa: {len(symbols)} mã ({symbols[0]}...{symbols[-1]})")
    return symbols


# ============================================================
# FETCH OHLCV TỪ VNDIRECT
# ============================================================

def fetch_stock_ohlcv(symbol: str, start: str, end: str) -> pd.DataFrame:
    """Lấy OHLCV lịch sử cho 1 mã từ VNDirect dchart API."""
    start_ts = int(datetime.strptime(start, "%Y-%m-%d").timestamp())
    end_ts = int((datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1)).timestamp())

    params = {
        "resolution": "D",
        "symbol": symbol,
        "from": start_ts,
        "to": end_ts,
    }

    try:
        resp = _session.get(_VND_CHART_URL, params=params, timeout=30)
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

CORE_COLS = ["time", "open", "high", "low", "close", "volume"]


def _process_one_stock(symbol: str, start: str, end: str, force_full: bool) -> dict:
    """Fetch + merge OHLCV cho 1 mã (chạy trong thread)."""
    csv_path = DATA_DIR / f"{symbol}.csv"
    existing_df = None
    fetch_start = start
    is_incremental = False

    # Check existing CSV for incremental update
    if not force_full and csv_path.exists():
        try:
            existing_df = pd.read_csv(csv_path, parse_dates=["time"])
            if not existing_df.empty and "time" in existing_df.columns:
                last_date = existing_df["time"].max()
                fetch_start = (last_date - timedelta(days=3)).strftime("%Y-%m-%d")
                is_incremental = True
            else:
                existing_df = None
        except Exception:
            existing_df = None

    try:
        new_data = fetch_stock_ohlcv(symbol, fetch_start, end)

        if new_data is not None and not new_data.empty:
            if existing_df is not None and not existing_df.empty:
                existing_core = existing_df[CORE_COLS].copy()
                combined = pd.concat([existing_core, new_data])
                combined = (
                    combined
                    .drop_duplicates("time", keep="last")
                    .sort_values("time")
                    .reset_index(drop=True)
                )
            else:
                combined = new_data

            combined = add_indicators(combined)
            combined["symbol"] = symbol
            combined.to_csv(csv_path, index=False, encoding="utf-8-sig")

            return {"status": "ok", "type": "incremental" if is_incremental else "full"}

        elif existing_df is not None and not existing_df.empty:
            return {"status": "ok", "type": "incremental"}
        else:
            return {"status": "error", "symbol": symbol}

    except Exception as e:
        return {"status": "error", "symbol": symbol, "msg": str(e)}


def collect_stocks(symbols: list, start: str, end: str, force_full: bool = False):
    """
    Thu thập OHLCV cho danh sách mã cổ phiếu (song song).

    Dùng ThreadPoolExecutor để fetch nhiều mã cùng lúc từ VNDirect API.
    Nếu file CSV đã tồn tại → chỉ fetch dữ liệu mới (incremental).
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    total = len(symbols)
    success = 0
    incremental = 0
    full_fetch = 0
    errors = []
    completed = 0

    logger.info(f"  Song song: {MAX_WORKERS} threads")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(_process_one_stock, sym, start, end, force_full): sym
            for sym in symbols
        }

        for future in as_completed(futures):
            completed += 1
            symbol = futures[future]

            if completed % BATCH_SIZE == 0 or completed == total:
                logger.info(
                    f"  [{completed}/{total}] "
                    f"(OK: {success}, incremental: {incremental}, full: {full_fetch}, lỗi: {len(errors)})"
                )

            try:
                result = future.result()
                if result["status"] == "ok":
                    success += 1
                    if result["type"] == "incremental":
                        incremental += 1
                    else:
                        full_fetch += 1
                else:
                    errors.append(result.get("symbol", symbol))
            except Exception as e:
                errors.append(symbol)
                logger.debug(f"  {symbol}: thread lỗi - {e}")

    logger.info(f"\nKết quả: {success}/{total} mã thành công")
    logger.info(f"  Incremental: {incremental} | Full fetch: {full_fetch} | Lỗi: {len(errors)}")
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
    parser.add_argument("--full", action="store_true",
                        help="Force fetch lại toàn bộ lịch sử (bỏ qua CSV cũ)")
    args = parser.parse_args()

    end = args.end or datetime.now().strftime("%Y-%m-%d")
    start = args.start or (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    # Initialize rate limiter (auto-detects tier from VNSTOCK_API_KEY)
    init_rate_limiter()

    # Count existing CSV files
    existing_count = len(list(DATA_DIR.glob("*.csv"))) if DATA_DIR.exists() else 0

    logger.info("=" * 60)
    logger.info("THU THẬP OHLCV CỔ PHIẾU")
    logger.info(f"Thời gian: {start} -> {end}")
    logger.info(f"Top: {args.top_n} vốn hóa lớn nhất")
    logger.info(f"Nguồn: VNDirect dchart API")
    logger.info(f"CSV đã có: {existing_count} files {'(sẽ cập nhật incremental)' if existing_count > 0 and not args.full else '(fetch full)'}")
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
    collect_stocks(symbols, start, end, force_full=args.full)

    logger.info("\n" + "=" * 60)
    logger.info("HOÀN TẤT!")
    logger.info(f"Dữ liệu: {DATA_DIR}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
