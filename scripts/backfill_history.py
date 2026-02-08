"""
Backfill dữ liệu lịch sử chứng khoán Việt Nam.

Lấy dữ liệu OHLCV lịch sử cho một khoảng thời gian, lưu vào:
    data/history/
    ├── ohlcv_all.csv          # Toàn bộ OHLCV gộp lại
    ├── sjc_gold_history.csv   # Giá vàng SJC theo ngày
    └── per_symbol/            # OHLCV từng mã riêng (tùy chọn)
        ├── VNM.csv
        ├── ACB.csv
        └── ...

Cách chạy:
    python scripts/backfill_history.py --start 2025-01-01 --end 2026-02-08
    python scripts/backfill_history.py --start 2025-01-01 --symbols VNM,ACB,FPT
    python scripts/backfill_history.py --start 2024-01-01 --end 2024-12-31 --per-symbol
"""

import sys
import os
import time
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

# ============================================================
# CẤU HÌNH
# ============================================================

DATA_DIR = PROJECT_ROOT / "data" / "history"
LOG_DIR = PROJECT_ROOT / "logs"

DEFAULT_SOURCE = "VCI"

# Golden Sponsor: 500 req/phút
BATCH_SIZE = 50
BATCH_DELAY = 0.5
REQUEST_DELAY = 0.12

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("backfill")


# ============================================================
# LẤY DỮ LIỆU
# ============================================================

def get_all_symbols(source: str = DEFAULT_SOURCE) -> list:
    """Lấy danh sách toàn bộ mã cổ phiếu."""
    from vnstock.common.client import Vnstock

    logger.info(f"Đang lấy danh sách mã từ {source}...")
    client = Vnstock(source=source, show_log=False)
    stock = client.stock(symbol="ACB", source=source)
    df = stock.listing.symbols_by_exchange(show_log=False)
    symbols = df["symbol"].tolist()
    logger.info(f"Tìm thấy {len(symbols)} mã.")
    return symbols


def fetch_ohlcv(symbol: str, start: str, end: str, source: str = DEFAULT_SOURCE) -> pd.DataFrame:
    """Lấy OHLCV lịch sử cho 1 mã trong khoảng thời gian."""
    from vnstock.common.client import Vnstock

    client = Vnstock(source=source, show_log=False)
    stock = client.stock(symbol=symbol, source=source)
    df = stock.quote.history(start=start, end=end, interval="1D")
    if df is not None and not df.empty:
        df["symbol"] = symbol
    return df


def fetch_sjc_gold_history(start: str, end: str) -> pd.DataFrame:
    """Lấy giá vàng SJC cho nhiều ngày."""
    from vnstock.explorer.misc.gold_price import sjc_gold_price

    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")

    all_data = []
    current = start_dt
    total_days = (end_dt - start_dt).days + 1
    processed = 0

    while current <= end_dt:
        # Bỏ qua cuối tuần
        if current.weekday() < 5:
            processed += 1
            date_str = current.strftime("%Y-%m-%d")

            if processed % 20 == 1:
                logger.info(f"  Giá vàng SJC: ngày {date_str} ({processed}/{total_days})...")

            try:
                df = sjc_gold_price(date=date_str)
                if df is not None and not df.empty:
                    all_data.append(df)
            except Exception:
                pass

            time.sleep(REQUEST_DELAY)

        current += timedelta(days=1)

    if all_data:
        result = pd.concat(all_data, ignore_index=True)
        logger.info(f"Đã lấy giá vàng SJC: {len(result)} dòng, {processed} ngày.")
        return result
    return pd.DataFrame()


# ============================================================
# BACKFILL CHÍNH
# ============================================================

def run_backfill(start: str, end: str, symbols: list, source: str, per_symbol: bool):
    """Chạy backfill dữ liệu lịch sử."""
    start_time = time.time()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    fh = logging.FileHandler(LOG_DIR / f"backfill_{start}_{end}.log", encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)

    logger.info("=" * 60)
    logger.info(f"BACKFILL DỮ LIỆU LỊCH SỬ")
    logger.info(f"Khoảng thời gian: {start} -> {end}")
    logger.info(f"Nguồn: {source}")
    logger.info("=" * 60)

    # Xác định danh sách mã
    if not symbols:
        symbols = get_all_symbols(source=source)
    logger.info(f"Số mã cổ phiếu: {len(symbols)}")

    # 1. Lấy OHLCV lịch sử
    logger.info("\n[1/2] LẤY DỮ LIỆU OHLCV LỊCH SỬ")
    all_data = []
    errors = []
    total = len(symbols)

    for idx, symbol in enumerate(symbols):
        if (idx + 1) % 20 == 0 or idx == 0:
            elapsed = time.time() - start_time
            logger.info(f"  {idx + 1}/{total} ({symbol}) - {elapsed:.0f}s elapsed")

        try:
            df = fetch_ohlcv(symbol, start, end, source)
            if df is not None and not df.empty:
                all_data.append(df)

                # Lưu từng mã riêng nếu cần
                if per_symbol:
                    symbol_dir = DATA_DIR / "per_symbol"
                    symbol_dir.mkdir(parents=True, exist_ok=True)
                    df.to_csv(symbol_dir / f"{symbol}.csv", index=False, encoding="utf-8-sig")
        except Exception as e:
            errors.append(symbol)
            if len(errors) <= 5:
                logger.debug(f"  Lỗi {symbol}: {e}")

        # Rate limiting
        if (idx + 1) % BATCH_SIZE == 0:
            time.sleep(BATCH_DELAY)
        else:
            time.sleep(REQUEST_DELAY)

    if errors:
        logger.warning(f"  {len(errors)} mã lỗi: {errors[:20]}{'...' if len(errors) > 20 else ''}")

    # Gộp và lưu
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        combined = combined.sort_values(["symbol", "time"]).reset_index(drop=True)
        filepath = DATA_DIR / "ohlcv_all.csv"
        combined.to_csv(filepath, index=False, encoding="utf-8-sig")
        logger.info(f"Đã lưu {filepath} ({len(combined)} dòng, {combined['symbol'].nunique()} mã)")
    else:
        logger.warning("Không lấy được dữ liệu OHLCV nào.")

    # 2. Giá vàng SJC lịch sử
    logger.info("\n[2/2] GIÁ VÀNG SJC LỊCH SỬ")
    gold_df = fetch_sjc_gold_history(start, end)
    if not gold_df.empty:
        gold_path = DATA_DIR / "sjc_gold_history.csv"
        gold_df.to_csv(gold_path, index=False, encoding="utf-8-sig")
        logger.info(f"Đã lưu {gold_path} ({len(gold_df)} dòng)")

    elapsed = time.time() - start_time
    logger.info("\n" + "=" * 60)
    logger.info(f"HOÀN TẤT! {elapsed:.0f}s ({elapsed/60:.1f} phút)")
    logger.info(f"Dữ liệu: {DATA_DIR}")
    logger.info("=" * 60)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Backfill dữ liệu lịch sử chứng khoán Việt Nam.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  python scripts/backfill_history.py --start 2025-01-01                        # Từ 2025 đến nay
  python scripts/backfill_history.py --start 2025-01-01 --end 2025-12-31       # Cả năm 2025
  python scripts/backfill_history.py --start 2025-01-01 --symbols VNM,ACB,FPT  # Chỉ 3 mã
  python scripts/backfill_history.py --start 2024-01-01 --per-symbol           # Lưu từng mã riêng
        """,
    )
    parser.add_argument("--start", required=True, help="Ngày bắt đầu (YYYY-MM-DD)")
    parser.add_argument("--end", default="", help="Ngày kết thúc (YYYY-MM-DD). Mặc định: hôm nay")
    parser.add_argument("--symbols", default="", help="Danh sách mã, ngăn bởi dấu phẩy. Mặc định: toàn bộ sàn")
    parser.add_argument("--source", default=DEFAULT_SOURCE, choices=["VCI", "KBS"], help="Nguồn dữ liệu")
    parser.add_argument("--per-symbol", action="store_true", help="Lưu từng mã ra file riêng")
    args = parser.parse_args()

    end = args.end or datetime.now().strftime("%Y-%m-%d")
    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()] if args.symbols else []

    run_backfill(start=args.start, end=end, symbols=symbols, source=args.source, per_symbol=args.per_symbol)


if __name__ == "__main__":
    main()
