"""
Script tự động thu thập dữ liệu chứng khoán Việt Nam và giá vàng SJC.

Chạy hàng ngày sau 15h (sau khi sàn đóng cửa) để lấy:
1. Danh sách toàn bộ mã cổ phiếu niêm yết (HOSE, HNX, UPCOM)
2. Dữ liệu OHLCV trong ngày của tất cả mã
3. Giá vàng SJC
4. Giá vàng BTMC
5. Tỷ giá ngoại tệ VCB

Dữ liệu được lưu vào thư mục data/ theo cấu trúc:
    data/
    ├── YYYY-MM-DD/
    │   ├── all_symbols.csv
    │   ├── daily_ohlcv.csv
    │   ├── price_board.csv
    │   ├── sjc_gold.csv
    │   ├── btmc_gold.csv
    │   └── exchange_rate.csv
    └── latest -> YYYY-MM-DD/  (symlink)

Cách chạy:
    python scripts/daily_collector.py                 # Chạy lần đầu, lấy dữ liệu hôm nay
    python scripts/daily_collector.py --date 2026-02-07  # Lấy dữ liệu ngày cụ thể
    python scripts/daily_collector.py --days-back 5      # Lấy 5 ngày gần nhất

Cài đặt chạy tự động:
    python scripts/daily_collector.py --install-cron     # Cài cron job 15:30 hàng ngày
    python scripts/daily_collector.py --remove-cron      # Gỡ cron job
"""

import sys
import os
import time
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Thêm thư mục gốc project vào path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

# ============================================================
# CẤU HÌNH
# ============================================================

DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"

# Nguồn dữ liệu mặc định
DEFAULT_SOURCE = "VCI"

# Golden Sponsor: 500 req/phút (~8 req/giây)
# Tăng batch size và giảm delay để tận dụng tối đa
BATCH_SIZE = 50         # Số mã cổ phiếu mỗi batch khi lấy OHLCV
BATCH_DELAY = 0.5       # Giây chờ giữa các batch
REQUEST_DELAY = 0.12    # Giây chờ giữa mỗi request (~8 req/s)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger("daily_collector")


def setup_file_logging(date_str: str):
    """Thêm file handler cho logging theo ngày."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(LOG_DIR / f"collector_{date_str}.log", encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)


# ============================================================
# THU THẬP DỮ LIỆU
# ============================================================

def get_all_symbols(source: str = DEFAULT_SOURCE) -> pd.DataFrame:
    """Lấy danh sách toàn bộ mã cổ phiếu niêm yết."""
    from vnstock.common.client import Vnstock

    logger.info(f"Đang lấy danh sách mã cổ phiếu từ {source}...")
    client = Vnstock(source=source, show_log=False)
    stock = client.stock(symbol="ACB", source=source)
    df = stock.listing.symbols_by_exchange(show_log=False)
    logger.info(f"Tìm thấy {len(df)} mã cổ phiếu.")
    return df


def get_daily_ohlcv_batch(symbols: list, date_str: str, source: str = DEFAULT_SOURCE) -> pd.DataFrame:
    """
    Lấy dữ liệu OHLCV trong ngày cho một danh sách mã cổ phiếu.

    Sử dụng price_board để lấy dữ liệu batch (nhanh hơn gọi từng mã).
    """
    from vnstock.common.client import Vnstock

    client = Vnstock(source=source, show_log=False)
    stock = client.stock(symbol=symbols[0], source=source)

    all_data = []
    total = len(symbols)

    for i in range(0, total, BATCH_SIZE):
        batch = symbols[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
        logger.info(f"  Batch {batch_num}/{total_batches}: {len(batch)} mã ({batch[0]}...{batch[-1]})")

        try:
            df = stock.trading.price_board(symbols_list=batch, show_log=False)
            if df is not None and not df.empty:
                all_data.append(df)
        except Exception as e:
            logger.warning(f"  Lỗi batch {batch_num}: {e}")

        if i + BATCH_SIZE < total:
            time.sleep(BATCH_DELAY)

    if all_data:
        result = pd.concat(all_data, ignore_index=True)
        logger.info(f"Đã lấy dữ liệu price board cho {len(result)} mã.")
        return result
    else:
        logger.warning("Không lấy được dữ liệu price board nào.")
        return pd.DataFrame()


def get_daily_ohlcv_history(symbols: list, date_str: str, source: str = DEFAULT_SOURCE) -> pd.DataFrame:
    """
    Lấy dữ liệu OHLCV lịch sử từng mã (chính xác hơn price_board).
    Dùng cho trường hợp cần dữ liệu OHLCV chuẩn.
    """
    from vnstock.common.client import Vnstock

    client = Vnstock(source=source, show_log=False)
    all_data = []
    total = len(symbols)
    errors = []

    for idx, symbol in enumerate(symbols):
        if (idx + 1) % 50 == 0 or idx == 0:
            logger.info(f"  Đang xử lý {idx + 1}/{total} ({symbol})...")

        try:
            stock = client.stock(symbol=symbol, source=source)
            df = stock.quote.history(start=date_str, end=date_str, interval="1D")
            if df is not None and not df.empty:
                df["symbol"] = symbol
                all_data.append(df)
        except Exception as e:
            errors.append(symbol)
            if len(errors) <= 10:
                logger.debug(f"  Lỗi {symbol}: {e}")

        # Rate limiting
        if (idx + 1) % BATCH_SIZE == 0:
            time.sleep(BATCH_DELAY)
        else:
            time.sleep(REQUEST_DELAY)

    if errors:
        logger.warning(f"  {len(errors)} mã bị lỗi: {errors[:20]}{'...' if len(errors) > 20 else ''}")

    if all_data:
        result = pd.concat(all_data, ignore_index=True)
        logger.info(f"Đã lấy OHLCV cho {len(result)} mã ({len(errors)} lỗi).")
        return result
    else:
        logger.warning("Không lấy được dữ liệu OHLCV nào.")
        return pd.DataFrame()


def get_sjc_gold(date_str: str) -> pd.DataFrame:
    """Lấy giá vàng SJC."""
    from vnstock.explorer.misc.gold_price import sjc_gold_price

    logger.info("Đang lấy giá vàng SJC...")
    try:
        df = sjc_gold_price(date=date_str)
        if df is not None and not df.empty:
            logger.info(f"Đã lấy {len(df)} dòng giá vàng SJC.")
            return df
        else:
            logger.warning("Không có dữ liệu giá vàng SJC.")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"Lỗi lấy giá vàng SJC: {e}")
        return pd.DataFrame()


def get_btmc_gold() -> pd.DataFrame:
    """Lấy giá vàng BTMC."""
    from vnstock.explorer.misc.gold_price import btmc_goldprice

    logger.info("Đang lấy giá vàng BTMC...")
    try:
        df = btmc_goldprice()
        if df is not None and not df.empty:
            logger.info(f"Đã lấy {len(df)} dòng giá vàng BTMC.")
            return df
        else:
            logger.warning("Không có dữ liệu giá vàng BTMC.")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"Lỗi lấy giá vàng BTMC: {e}")
        return pd.DataFrame()


def get_exchange_rate(date_str: str) -> pd.DataFrame:
    """Lấy tỷ giá ngoại tệ VCB."""
    from vnstock.explorer.misc.exchange_rate import vcb_exchange_rate

    logger.info("Đang lấy tỷ giá VCB...")
    try:
        df = vcb_exchange_rate(date=date_str)
        if df is not None and not df.empty:
            logger.info(f"Đã lấy {len(df)} dòng tỷ giá.")
            return df
        else:
            logger.warning("Không có dữ liệu tỷ giá.")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"Lỗi lấy tỷ giá: {e}")
        return pd.DataFrame()


# ============================================================
# LƯU DỮ LIỆU
# ============================================================

def save_data(df: pd.DataFrame, date_dir: Path, filename: str):
    """Lưu DataFrame ra file CSV."""
    if df is None or df.empty:
        logger.info(f"  Bỏ qua {filename} (không có dữ liệu).")
        return

    filepath = date_dir / filename
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    logger.info(f"  Đã lưu {filepath} ({len(df)} dòng)")


def update_latest_symlink(date_dir: Path):
    """Cập nhật symlink latest/ trỏ đến thư mục ngày mới nhất."""
    latest_link = DATA_DIR / "latest"
    if latest_link.is_symlink() or latest_link.exists():
        latest_link.unlink()
    latest_link.symlink_to(date_dir.name, target_is_directory=True)
    logger.info(f"Đã cập nhật symlink latest -> {date_dir.name}")


# ============================================================
# COLLECTOR CHÍNH
# ============================================================

def collect_daily_data(date_str: str, source: str = DEFAULT_SOURCE, skip_ohlcv_history: bool = False):
    """
    Thu thập toàn bộ dữ liệu cho một ngày.

    Args:
        date_str: Ngày thu thập (YYYY-MM-DD)
        source: Nguồn dữ liệu (VCI, KBS)
        skip_ohlcv_history: Bỏ qua lấy OHLCV từng mã (chỉ dùng price_board)
    """
    start_time = time.time()

    # Tạo thư mục
    date_dir = DATA_DIR / date_str
    date_dir.mkdir(parents=True, exist_ok=True)

    setup_file_logging(date_str)

    logger.info("=" * 60)
    logger.info(f"THU THẬP DỮ LIỆU NGÀY {date_str}")
    logger.info(f"Nguồn: {source} | Thư mục: {date_dir}")
    logger.info("=" * 60)

    # 1. Danh sách mã cổ phiếu
    logger.info("\n[1/5] DANH SÁCH MÃ CỔ PHIẾU")
    symbols_df = get_all_symbols(source=source)
    save_data(symbols_df, date_dir, "all_symbols.csv")

    if symbols_df.empty:
        logger.error("Không lấy được danh sách mã. Dừng lại.")
        return

    # Lọc chỉ lấy cổ phiếu (loại bỏ ETF, CW, bond nếu có)
    stock_symbols = symbols_df["symbol"].tolist()
    logger.info(f"Tổng số mã sẽ xử lý: {len(stock_symbols)}")

    # 2. Bảng giá (price board) - nhanh, lấy batch
    logger.info("\n[2/5] BẢNG GIÁ (PRICE BOARD)")
    price_board_df = get_daily_ohlcv_batch(stock_symbols, date_str, source=source)
    save_data(price_board_df, date_dir, "price_board.csv")

    # 3. OHLCV lịch sử từng mã (tùy chọn, chậm hơn nhưng chính xác)
    if not skip_ohlcv_history:
        logger.info("\n[3/5] DỮ LIỆU OHLCV LỊCH SỬ")
        ohlcv_df = get_daily_ohlcv_history(stock_symbols, date_str, source=source)
        save_data(ohlcv_df, date_dir, "daily_ohlcv.csv")
    else:
        logger.info("\n[3/5] DỮ LIỆU OHLCV LỊCH SỬ - BỎ QUA (--skip-ohlcv)")

    # 4. Giá vàng
    logger.info("\n[4/5] GIÁ VÀNG")
    sjc_df = get_sjc_gold(date_str)
    save_data(sjc_df, date_dir, "sjc_gold.csv")

    time.sleep(REQUEST_DELAY)

    btmc_df = get_btmc_gold()
    save_data(btmc_df, date_dir, "btmc_gold.csv")

    # 5. Tỷ giá
    logger.info("\n[5/5] TỶ GIÁ NGOẠI TỆ")
    fx_df = get_exchange_rate(date_str)
    save_data(fx_df, date_dir, "exchange_rate.csv")

    # Cập nhật symlink
    update_latest_symlink(date_dir)

    elapsed = time.time() - start_time
    logger.info("\n" + "=" * 60)
    logger.info(f"HOÀN TẤT! Thời gian: {elapsed:.1f}s ({elapsed/60:.1f} phút)")
    logger.info(f"Dữ liệu lưu tại: {date_dir}")
    logger.info("=" * 60)


# ============================================================
# QUẢN LÝ CRON JOB
# ============================================================

def install_cron(hour: int = 15, minute: int = 30):
    """Cài đặt cron job chạy hàng ngày."""
    import subprocess

    python_path = sys.executable
    script_path = Path(__file__).resolve()

    cron_line = f"{minute} {hour} * * 1-5 cd {PROJECT_ROOT} && {python_path} {script_path} >> {LOG_DIR}/cron.log 2>&1"
    cron_comment = "# vnstock daily collector"

    # Đọc crontab hiện tại
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout if result.returncode == 0 else ""

    # Kiểm tra đã có chưa
    if str(script_path) in existing:
        logger.info("Cron job đã tồn tại. Đang cập nhật...")
        lines = [l for l in existing.strip().split("\n")
                 if str(script_path) not in l and "vnstock daily collector" not in l]
        existing = "\n".join(lines) + "\n" if lines else ""

    new_crontab = existing.rstrip("\n") + f"\n{cron_comment}\n{cron_line}\n"

    proc = subprocess.run(["crontab", "-"], input=new_crontab, capture_output=True, text=True)
    if proc.returncode == 0:
        logger.info(f"Đã cài cron job: {cron_line}")
        logger.info(f"Script sẽ chạy lúc {hour}:{minute:02d} thứ 2-6 hàng tuần.")
    else:
        logger.error(f"Lỗi cài cron: {proc.stderr}")


def remove_cron():
    """Gỡ bỏ cron job."""
    import subprocess

    script_path = str(Path(__file__).resolve())

    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if result.returncode != 0:
        logger.info("Không có crontab nào.")
        return

    lines = [l for l in result.stdout.strip().split("\n")
             if script_path not in l and "vnstock daily collector" not in l]
    new_crontab = "\n".join(lines) + "\n" if lines else ""

    proc = subprocess.run(["crontab", "-"], input=new_crontab, capture_output=True, text=True)
    if proc.returncode == 0:
        logger.info("Đã gỡ cron job.")
    else:
        logger.error(f"Lỗi gỡ cron: {proc.stderr}")


# ============================================================
# CLI
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Thu thập dữ liệu chứng khoán Việt Nam và giá vàng hàng ngày.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  python scripts/daily_collector.py                        # Lấy dữ liệu hôm nay
  python scripts/daily_collector.py --date 2026-02-07      # Lấy ngày cụ thể
  python scripts/daily_collector.py --days-back 5          # Lấy 5 ngày gần nhất
  python scripts/daily_collector.py --skip-ohlcv           # Chỉ lấy price board (nhanh)
  python scripts/daily_collector.py --source KBS           # Dùng nguồn KBS
  python scripts/daily_collector.py --install-cron         # Cài cron 15:30 hàng ngày
  python scripts/daily_collector.py --install-cron --hour 16 --minute 0  # Cài cron 16:00
  python scripts/daily_collector.py --remove-cron          # Gỡ cron
        """,
    )
    parser.add_argument("--date", type=str, default=None,
                        help="Ngày thu thập (YYYY-MM-DD). Mặc định: hôm nay")
    parser.add_argument("--days-back", type=int, default=0,
                        help="Lấy dữ liệu N ngày gần nhất")
    parser.add_argument("--source", type=str, default=DEFAULT_SOURCE,
                        choices=["VCI", "KBS"],
                        help=f"Nguồn dữ liệu (mặc định: {DEFAULT_SOURCE})")
    parser.add_argument("--skip-ohlcv", action="store_true",
                        help="Bỏ qua lấy OHLCV từng mã (chỉ lấy price board)")
    parser.add_argument("--install-cron", action="store_true",
                        help="Cài đặt cron job chạy tự động")
    parser.add_argument("--remove-cron", action="store_true",
                        help="Gỡ bỏ cron job")
    parser.add_argument("--hour", type=int, default=15,
                        help="Giờ chạy cron (mặc định: 15)")
    parser.add_argument("--minute", type=int, default=30,
                        help="Phút chạy cron (mặc định: 30)")
    return parser.parse_args()


def main():
    args = parse_args()

    # Quản lý cron
    if args.install_cron:
        install_cron(hour=args.hour, minute=args.minute)
        return

    if args.remove_cron:
        remove_cron()
        return

    # Xác định ngày thu thập
    if args.days_back > 0:
        dates = []
        for i in range(args.days_back):
            d = datetime.now() - timedelta(days=i)
            # Bỏ qua thứ 7, CN
            if d.weekday() < 5:
                dates.append(d.strftime("%Y-%m-%d"))
        logger.info(f"Sẽ thu thập {len(dates)} ngày: {dates}")
        for date_str in reversed(dates):
            collect_daily_data(date_str, source=args.source, skip_ohlcv_history=args.skip_ohlcv)
    else:
        date_str = args.date or datetime.now().strftime("%Y-%m-%d")
        collect_daily_data(date_str, source=args.source, skip_ohlcv_history=args.skip_ohlcv)


if __name__ == "__main__":
    main()
