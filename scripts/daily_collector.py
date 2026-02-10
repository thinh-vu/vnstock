"""
Script tự động thu thập dữ liệu chứng khoán Việt Nam cho Dashboard.

Chạy hàng ngày sau 15h (sau khi sàn đóng cửa) để lấy:
1. Bảng giá (price board) toàn bộ mã
2. Top 30 cổ phiếu tăng/giảm mạnh nhất (trong top 500 vốn hóa)
3. Market breadth (số mã tăng/giảm/đứng giá)
4. Foreign flow (khối ngoại mua/bán ròng)
5. Index impact (cổ phiếu ảnh hưởng VNINDEX)

Dữ liệu được lưu vào thư mục data/ theo cấu trúc:
    data/
    ├── YYYY-MM-DD/
    │   ├── price_board.csv
    │   ├── top_gainers.csv
    │   ├── top_losers.csv
    │   ├── market_breadth.csv
    │   ├── foreign_flow.csv
    │   ├── foreign_top_buy.csv
    │   ├── foreign_top_sell.csv
    │   ├── index_impact_positive.csv
    │   └── index_impact_negative.csv
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
    Sử dụng SQLite cache: bỏ qua mã đã có dữ liệu trong cache cho ngày này.
    """
    from vnstock.common.client import Vnstock
    from db_cache import get_cached_stock, save_stock_data

    client = Vnstock(source=source, show_log=False)
    all_data = []
    total = len(symbols)
    errors = []
    cached_count = 0
    api_count = 0

    for idx, symbol in enumerate(symbols):
        if (idx + 1) % 100 == 0 or idx == 0:
            logger.info(f"  Đang xử lý {idx + 1}/{total} ({symbol})... (cache: {cached_count}, API: {api_count})")

        # Kiểm tra cache trước
        cached = get_cached_stock(symbol, date_str, date_str)
        if not cached.empty:
            cached["symbol"] = symbol
            all_data.append(cached)
            cached_count += 1
            continue

        # Chưa có trong cache → gọi API
        try:
            stock = client.stock(symbol=symbol, source=source)
            df = stock.quote.history(start=date_str, end=date_str, interval="1D")
            if df is not None and not df.empty:
                df["symbol"] = symbol
                all_data.append(df)
                save_stock_data(symbol, df)
                api_count += 1
        except Exception as e:
            errors.append(symbol)
            if len(errors) <= 10:
                logger.debug(f"  Lỗi {symbol}: {e}")

        # Rate limiting (chỉ khi gọi API)
        if (api_count) % BATCH_SIZE == 0 and api_count > 0:
            time.sleep(BATCH_DELAY)
        else:
            time.sleep(REQUEST_DELAY)

    if errors:
        logger.warning(f"  {len(errors)} mã bị lỗi: {errors[:20]}{'...' if len(errors) > 20 else ''}")

    logger.info(f"OHLCV: {len(all_data)} mã (cache: {cached_count}, API: {api_count}, lỗi: {len(errors)})")

    if all_data:
        result = pd.concat(all_data, ignore_index=True)
        return result
    else:
        logger.warning("Không lấy được dữ liệu OHLCV nào.")
        return pd.DataFrame()


def fetch_kbs_full_board(stock_symbols: list) -> pd.DataFrame:
    """
    Fetch bảng giá KBS đầy đủ cho toàn bộ mã cổ phiếu.
    Dữ liệu này được dùng chung cho: top movers, market breadth, foreign flow.

    Returns:
        DataFrame with all KBS price_board columns (get_all=True).
    """
    from vnstock.common.client import Vnstock

    logger.info(f"Đang lấy bảng giá KBS ({len(stock_symbols)} mã)...")
    client = Vnstock(source="KBS", show_log=False)
    stock = client.stock(symbol="ACB", source="KBS")

    all_data = []
    total = len(stock_symbols)
    for i in range(0, total, BATCH_SIZE):
        batch = stock_symbols[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

        try:
            df = stock.trading.price_board(symbols_list=batch, get_all=True)
            if df is not None and not df.empty:
                all_data.append(df)
        except Exception as e:
            logger.warning(f"  KBS batch {batch_num}/{total_batches} lỗi: {e}")

        if i + BATCH_SIZE < total:
            time.sleep(BATCH_DELAY)

    if not all_data:
        logger.warning("Không lấy được dữ liệu bảng giá KBS.")
        return pd.DataFrame()

    board = pd.concat(all_data, ignore_index=True)
    logger.info(f"Bảng giá KBS: {len(board)} mã")

    # Ensure numeric types for key columns
    numeric_cols = ['close_price', 'percent_change', 'total_value', 'total_trades',
                    'foreign_buy_volume', 'foreign_sell_volume',
                    'total_listed_qty', 'listed_shares']
    for col in numeric_cols:
        if col in board.columns:
            board[col] = pd.to_numeric(board[col], errors='coerce')

    return board


def get_top_movers(board: pd.DataFrame, top_n: int = 500, movers_n: int = 30):
    """
    Lấy top cổ phiếu tăng/giảm mạnh nhất trong top N vốn hóa lớn nhất.

    Args:
        board: KBS price_board DataFrame (from fetch_kbs_full_board)
        top_n: Số mã vốn hóa lớn nhất để lọc
        movers_n: Số mã tăng/giảm mạnh nhất

    Returns:
        (top_gainers_df, top_losers_df)
    """
    if board.empty:
        return pd.DataFrame(), pd.DataFrame()

    df = board.copy()

    # Compute market_cap for ranking (close_price * listed shares)
    shares_col = None
    for col in ['total_listed_qty', 'listed_shares']:
        if col in df.columns:
            shares_col = col
            break

    if shares_col and 'close_price' in df.columns:
        df['market_cap'] = df['close_price'] * df[shares_col]
        logger.info(f"  Market cap computed from close_price * {shares_col}")
    elif 'total_value' in df.columns:
        df['market_cap'] = df['total_value']
        logger.info("  Market cap approximated from total_value")
    else:
        logger.warning("  Không tìm thấy cột để tính vốn hóa, lấy toàn bộ")
        df['market_cap'] = 1

    # Filter top N by market cap
    df = df.dropna(subset=['market_cap', 'percent_change'])
    df = df[df['market_cap'] > 0]
    top_cap = df.nlargest(top_n, 'market_cap')
    logger.info(f"  Top {top_n} vốn hóa: {len(top_cap)} mã")

    # Filter valid percent_change (exclude 0 = giá đứng)
    valid = top_cap[top_cap['percent_change'] != 0].copy()

    # Convert close_price from KBS raw units (VND * 1000) to VND
    if 'close_price' in valid.columns:
        valid['close_price'] = valid['close_price'] / 1000

    # Select output columns
    out_cols = ['symbol', 'close_price', 'percent_change', 'total_trades', 'total_value']
    out_cols = [c for c in out_cols if c in valid.columns]

    # Top gainers (tăng mạnh nhất)
    gainers = valid.nlargest(movers_n, 'percent_change')[out_cols].reset_index(drop=True)
    gainers.index = gainers.index + 1
    gainers.index.name = 'rank'

    # Top losers (giảm mạnh nhất)
    losers = valid.nsmallest(movers_n, 'percent_change')[out_cols].reset_index(drop=True)
    losers.index = losers.index + 1
    losers.index.name = 'rank'

    if not gainers.empty:
        top = gainers.iloc[0]
        logger.info(f"  Top tăng: {top['symbol']} ({top['percent_change']:+.2f}%)")
    if not losers.empty:
        bot = losers.iloc[0]
        logger.info(f"  Top giảm: {bot['symbol']} ({bot['percent_change']:+.2f}%)")

    return gainers, losers


def compute_market_breadth(board: pd.DataFrame) -> pd.DataFrame:
    """
    Tính market breadth (độ rộng thị trường) từ bảng giá KBS.

    Đếm số mã tăng/giảm/đứng giá theo từng sàn (HOSE, HNX, UPCOM) và tổng.

    Returns:
        DataFrame with columns: exchange, advancing, declining, unchanged,
                                total_stocks, advance_decline_ratio
    """
    if board.empty or 'percent_change' not in board.columns:
        logger.warning("Không có dữ liệu percent_change để tính market breadth.")
        return pd.DataFrame()

    df = board.copy()

    # Classify each stock
    df['_status'] = 'unchanged'
    df.loc[df['percent_change'] > 0, '_status'] = 'advancing'
    df.loc[df['percent_change'] < 0, '_status'] = 'declining'

    rows = []

    # Per-exchange breadth
    exchanges = ['HOSE', 'HNX', 'UPCOM']
    if 'exchange' in df.columns:
        for ex in exchanges:
            ex_df = df[df['exchange'] == ex]
            if ex_df.empty:
                continue
            adv = (ex_df['_status'] == 'advancing').sum()
            dec = (ex_df['_status'] == 'declining').sum()
            unc = (ex_df['_status'] == 'unchanged').sum()
            total = len(ex_df)
            rows.append({
                'exchange': ex,
                'advancing': int(adv),
                'declining': int(dec),
                'unchanged': int(unc),
                'total_stocks': int(total),
                'net_ad': int(adv - dec),
            })

    # Total across all exchanges
    adv = (df['_status'] == 'advancing').sum()
    dec = (df['_status'] == 'declining').sum()
    unc = (df['_status'] == 'unchanged').sum()
    total = len(df)
    rows.append({
        'exchange': 'ALL',
        'advancing': int(adv),
        'declining': int(dec),
        'unchanged': int(unc),
        'total_stocks': int(total),
        'net_ad': int(adv - dec),
    })

    result = pd.DataFrame(rows)

    # Log summary
    all_row = result[result['exchange'] == 'ALL'].iloc[0]
    logger.info(
        f"  Market breadth: {all_row['advancing']} tăng / "
        f"{all_row['declining']} giảm / {all_row['unchanged']} đứng "
        f"(net A/D: {all_row['net_ad']:+d})"
    )

    return result


def compute_foreign_flow(board: pd.DataFrame, top_n: int = 20):
    """
    Tính dòng tiền khối ngoại từ bảng giá KBS.

    Returns:
        (flow_summary_df, top_net_buy_df, top_net_sell_df)
        - flow_summary: aggregate mua/bán ròng theo sàn
        - top_net_buy: top N mã khối ngoại mua ròng nhiều nhất
        - top_net_sell: top N mã khối ngoại bán ròng nhiều nhất
    """
    buy_col = 'foreign_buy_volume'
    sell_col = 'foreign_sell_volume'

    if board.empty or buy_col not in board.columns or sell_col not in board.columns:
        logger.warning("Không có dữ liệu foreign buy/sell volume.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    df = board.copy()
    df[buy_col] = df[buy_col].fillna(0)
    df[sell_col] = df[sell_col].fillna(0)
    df['foreign_net_volume'] = df[buy_col] - df[sell_col]

    # Compute foreign net value (volume * close_price)
    if 'close_price' in df.columns:
        df['foreign_buy_value'] = df[buy_col] * df['close_price']
        df['foreign_sell_value'] = df[sell_col] * df['close_price']
        df['foreign_net_value'] = df['foreign_buy_value'] - df['foreign_sell_value']

    # ---- 1. Aggregate per exchange ----
    rows = []
    exchanges = ['HOSE', 'HNX', 'UPCOM']
    if 'exchange' in df.columns:
        for ex in exchanges:
            ex_df = df[df['exchange'] == ex]
            if ex_df.empty:
                continue
            row = {
                'exchange': ex,
                'foreign_buy_volume': int(ex_df[buy_col].sum()),
                'foreign_sell_volume': int(ex_df[sell_col].sum()),
                'foreign_net_volume': int(ex_df['foreign_net_volume'].sum()),
            }
            if 'foreign_net_value' in ex_df.columns:
                row['foreign_buy_value'] = float(ex_df['foreign_buy_value'].sum())
                row['foreign_sell_value'] = float(ex_df['foreign_sell_value'].sum())
                row['foreign_net_value'] = float(ex_df['foreign_net_value'].sum())
            rows.append(row)

    # Total
    total_row = {
        'exchange': 'ALL',
        'foreign_buy_volume': int(df[buy_col].sum()),
        'foreign_sell_volume': int(df[sell_col].sum()),
        'foreign_net_volume': int(df['foreign_net_volume'].sum()),
    }
    if 'foreign_net_value' in df.columns:
        total_row['foreign_buy_value'] = float(df['foreign_buy_value'].sum())
        total_row['foreign_sell_value'] = float(df['foreign_sell_value'].sum())
        total_row['foreign_net_value'] = float(df['foreign_net_value'].sum())
    rows.append(total_row)

    flow_summary = pd.DataFrame(rows)

    # ---- 2. Top N net buyers/sellers ----
    # Filter stocks with meaningful foreign activity
    active = df[df['foreign_net_volume'] != 0].copy()

    value_col = 'foreign_net_value' if 'foreign_net_value' in active.columns else 'foreign_net_volume'
    out_cols = ['symbol', 'exchange', 'close_price',
                'foreign_buy_volume', 'foreign_sell_volume', 'foreign_net_volume']
    if 'foreign_net_value' in active.columns:
        out_cols.append('foreign_net_value')
    out_cols = [c for c in out_cols if c in active.columns]

    # Convert close_price from KBS raw (VND * 1000) to VND for display
    if 'close_price' in active.columns:
        active['close_price'] = active['close_price'] / 1000

    top_buy = active.nlargest(top_n, value_col)[out_cols].reset_index(drop=True)
    top_buy.index = top_buy.index + 1
    top_buy.index.name = 'rank'

    top_sell = active.nsmallest(top_n, value_col)[out_cols].reset_index(drop=True)
    top_sell.index = top_sell.index + 1
    top_sell.index.name = 'rank'

    # Log summary
    net = total_row['foreign_net_volume']
    direction = "MUA RÒNG" if net > 0 else "BÁN RÒNG"
    logger.info(f"  Foreign flow: {direction} {abs(net):,.0f} CP")
    if 'foreign_net_value' in total_row:
        net_val = total_row['foreign_net_value']
        logger.info(f"  Foreign net value: {net_val/1e9:,.1f} tỷ VND (KBS units)")
    if not top_buy.empty:
        t = top_buy.iloc[0]
        logger.info(f"  Top NN mua: {t['symbol']} (net: {t['foreign_net_volume']:+,.0f})")
    if not top_sell.empty:
        t = top_sell.iloc[0]
        logger.info(f"  Top NN bán: {t['symbol']} (net: {t['foreign_net_volume']:+,.0f})")

    return flow_summary, top_buy, top_sell


def compute_index_impact(board: pd.DataFrame, top_n: int = 20):
    """
    Tính cổ phiếu ảnh hưởng lớn nhất đến chỉ số (index drivers).

    Xấp xỉ impact = market_cap * price_change (tỷ trọng vốn hóa * biến động giá).
    Chỉ tính cho sàn HOSE (ảnh hưởng VNINDEX).

    Returns:
        (top_positive_df, top_negative_df)
        - top_positive: top N mã đóng góp tích cực nhất (kéo tăng)
        - top_negative: top N mã đóng góp tiêu cực nhất (kéo giảm)
    """
    if board.empty:
        return pd.DataFrame(), pd.DataFrame()

    df = board.copy()

    # Chỉ tính cho HOSE (VNINDEX)
    if 'exchange' in df.columns:
        df = df[df['exchange'] == 'HOSE'].copy()

    if df.empty or 'percent_change' not in df.columns or 'close_price' not in df.columns:
        logger.warning("Không đủ dữ liệu để tính index impact.")
        return pd.DataFrame(), pd.DataFrame()

    # Compute market_cap
    shares_col = None
    for col in ['total_listed_qty', 'listed_shares']:
        if col in df.columns:
            shares_col = col
            break

    if not shares_col:
        logger.warning("Không tìm thấy cột listed shares để tính impact.")
        return pd.DataFrame(), pd.DataFrame()

    df['market_cap'] = df['close_price'] * df[shares_col]
    df = df.dropna(subset=['market_cap', 'percent_change'])
    df = df[df['market_cap'] > 0]

    # Impact ~ market_cap * price_change (absolute change, not percent)
    # price_change from KBS = giá thay đổi (VND * 1000)
    if 'price_change' in df.columns:
        df['price_change'] = pd.to_numeric(df['price_change'], errors='coerce').fillna(0)
        df['impact'] = df['market_cap'] * df['price_change']
    else:
        # Fallback: use percent_change * market_cap
        df['impact'] = df['market_cap'] * df['percent_change'] / 100

    # Convert close_price to VND for display
    df['close_price'] = df['close_price'] / 1000

    out_cols = ['symbol', 'close_price', 'percent_change', 'market_cap', 'impact']
    out_cols = [c for c in out_cols if c in df.columns]

    # Filter stocks with non-zero impact
    active = df[df['impact'] != 0].copy()

    # Top positive impact (kéo tăng)
    top_pos = active.nlargest(top_n, 'impact')[out_cols].reset_index(drop=True)
    top_pos.index = top_pos.index + 1
    top_pos.index.name = 'rank'

    # Top negative impact (kéo giảm)
    top_neg = active.nsmallest(top_n, 'impact')[out_cols].reset_index(drop=True)
    top_neg.index = top_neg.index + 1
    top_neg.index.name = 'rank'

    if not top_pos.empty:
        t = top_pos.iloc[0]
        logger.info(f"  Top kéo tăng: {t['symbol']} ({t['percent_change']:+.2f}%)")
    if not top_neg.empty:
        t = top_neg.iloc[0]
        logger.info(f"  Top kéo giảm: {t['symbol']} ({t['percent_change']:+.2f}%)")

    return top_pos, top_neg


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

    # Lấy danh sách mã cổ phiếu (nội bộ, không lưu file)
    logger.info("\nLấy danh sách mã cổ phiếu...")
    symbols_df = get_all_symbols(source=source)

    if symbols_df.empty:
        logger.error("Không lấy được danh sách mã. Dừng lại.")
        return

    stock_symbols = symbols_df["symbol"].tolist()
    logger.info(f"Tổng số mã: {len(stock_symbols)}")

    # 1. Bảng giá (price board) - nhanh, lấy batch
    logger.info("\n[1/6] BẢNG GIÁ (PRICE BOARD)")
    price_board_df = get_daily_ohlcv_batch(stock_symbols, date_str, source=source)
    save_data(price_board_df, date_dir, "price_board.csv")

    # 2. KBS price_board → dùng chung cho top movers, breadth, foreign flow, impact
    logger.info("\n[2/6] BẢNG GIÁ KBS (cho top movers, breadth, foreign flow, impact)")
    kbs_board = pd.DataFrame()
    try:
        kbs_board = fetch_kbs_full_board(stock_symbols)
    except Exception as e:
        logger.error(f"Lỗi fetch KBS price_board: {e}")

    # 3. Top cổ phiếu tăng/giảm (trong top 500 vốn hóa)
    logger.info("\n[3/6] TOP TĂNG/GIẢM (TOP 500 VỐN HÓA)")
    try:
        gainers_df, losers_df = get_top_movers(kbs_board, top_n=500, movers_n=30)
        save_data(gainers_df, date_dir, "top_gainers.csv")
        save_data(losers_df, date_dir, "top_losers.csv")
    except Exception as e:
        logger.error(f"Lỗi lấy top movers: {e}")

    # 4. Market breadth
    logger.info("\n[4/6] MARKET BREADTH (ĐỘ RỘNG THỊ TRƯỜNG)")
    try:
        breadth_df = compute_market_breadth(kbs_board)
        save_data(breadth_df, date_dir, "market_breadth.csv")
    except Exception as e:
        logger.error(f"Lỗi tính market breadth: {e}")

    # 5. Foreign flow
    logger.info("\n[5/6] FOREIGN FLOW (DÒNG TIỀN KHỐI NGOẠI)")
    try:
        flow_df, top_buy_df, top_sell_df = compute_foreign_flow(kbs_board, top_n=20)
        save_data(flow_df, date_dir, "foreign_flow.csv")
        save_data(top_buy_df, date_dir, "foreign_top_buy.csv")
        save_data(top_sell_df, date_dir, "foreign_top_sell.csv")
    except Exception as e:
        logger.error(f"Lỗi tính foreign flow: {e}")

    # 6. Index impact
    logger.info("\n[6/6] INDEX IMPACT (CỔ PHIẾU ẢNH HƯỞNG CHỈ SỐ)")
    try:
        impact_pos_df, impact_neg_df = compute_index_impact(kbs_board, top_n=20)
        save_data(impact_pos_df, date_dir, "index_impact_positive.csv")
        save_data(impact_neg_df, date_dir, "index_impact_negative.csv")
    except Exception as e:
        logger.error(f"Lỗi tính index impact: {e}")

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
