"""
Thu thập dữ liệu tài chính cho top 500 cổ phiếu vốn hóa lớn nhất.

Nguồn: VCI API (hỗ trợ tiếng Anh, đầy đủ nhất).
Dữ liệu chỉ thay đổi theo quý → chạy hàng tuần hoặc khi cần.

Output:
    data/financials/
    ├── VCB/
    │   ├── balance_sheet.csv
    │   ├── income_statement.csv
    │   ├── cash_flow.csv
    │   └── ratios.csv
    ├── FPT/
    │   └── ...
    └── ... (500 thư mục)

Cách chạy:
    python scripts/collect_financials.py                   # Top 500, year + quarter
    python scripts/collect_financials.py --top-n 100       # Top 100
    python scripts/collect_financials.py --period year      # Chỉ lấy năm
"""

import sys
import time
import logging
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

# ============================================================
# CẤU HÌNH
# ============================================================

DATA_DIR = PROJECT_ROOT / "data" / "financials"
REQUEST_DELAY = 0.15  # ~7 req/s
SOURCE = "VCI"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("financials")

# Các loại báo cáo cần lấy
REPORT_TYPES = [
    ("balance_sheet", "Bảng CĐKT"),
    ("income_statement", "KQKD"),
    ("cash_flow", "Lưu chuyển tiền tệ"),
    ("ratio", "Chỉ số tài chính"),
]


# ============================================================
# LẤY TOP N VỐN HÓA (tái sử dụng từ collect_stocks.py)
# ============================================================

def get_top_symbols(top_n: int = 500) -> list:
    """Lấy top N mã vốn hóa lớn nhất từ KBS price_board."""
    from vnstock.common.client import Vnstock

    logger.info("Đang lấy danh sách mã cổ phiếu...")
    client = Vnstock(source="VCI", show_log=False)
    stock = client.stock(symbol="ACB", source="VCI")
    symbols_df = stock.listing.symbols_by_exchange(show_log=False)
    all_symbols = symbols_df["symbol"].tolist()
    logger.info(f"Tổng: {len(all_symbols)} mã")

    logger.info("Đang xếp hạng vốn hóa từ KBS...")
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
        logger.warning("Không lấy được KBS board, dùng thứ tự mặc định.")
        return all_symbols[:top_n]

    board = pd.concat(all_data, ignore_index=True)
    logger.info(f"KBS board: {len(board)} mã, columns: {list(board.columns)[:15]}")

    for col in ['close_price', 'listed_shares', 'total_listed_qty']:
        if col in board.columns:
            board[col] = pd.to_numeric(board[col], errors='coerce')

    shares_col = None
    for col in ['total_listed_qty', 'listed_shares']:
        if col in board.columns and board[col].sum() > 0:
            shares_col = col
            break

    if shares_col and 'close_price' in board.columns:
        board['market_cap'] = board['close_price'] * board[shares_col]
        logger.info(f"Market cap: close_price * {shares_col}")
    elif 'total_value' in board.columns:
        board['total_value'] = pd.to_numeric(board['total_value'], errors='coerce')
        board['market_cap'] = board['total_value']
        logger.info("Market cap: fallback to total_value")
    else:
        logger.warning("Không tính được market cap, dùng thứ tự mặc định.")
        return all_symbols[:top_n]

    board = board.dropna(subset=['market_cap'])
    board = board[board['market_cap'] > 0]
    top = board.nlargest(top_n, 'market_cap')
    symbols = top['symbol'].tolist()
    logger.info(f"Top {top_n} vốn hóa: {len(symbols)} mã")
    return symbols


# ============================================================
# FETCH DỮ LIỆU TÀI CHÍNH
# ============================================================

def fetch_financials(symbol: str, period: str = 'year') -> dict:
    """
    Lấy toàn bộ báo cáo tài chính cho 1 mã từ VCI.

    Returns:
        dict {report_name: DataFrame}
    """
    from vnstock.common.client import Vnstock

    client = Vnstock(source=SOURCE, show_log=False)
    stock = client.stock(symbol=symbol, source=SOURCE)

    results = {}

    for report_name, label in REPORT_TYPES:
        try:
            if report_name == "balance_sheet":
                df = stock.finance.balance_sheet(period=period, lang='en', dropna=True, show_log=False)
            elif report_name == "income_statement":
                df = stock.finance.income_statement(period=period, lang='en', dropna=True, show_log=False)
            elif report_name == "cash_flow":
                df = stock.finance.cash_flow(period=period, lang='en', dropna=True, show_log=False)
            elif report_name == "ratio":
                df = stock.finance.ratio(period=period, lang='en', dropna=True, show_log=False)
            else:
                continue

            if df is not None and not df.empty:
                results[report_name] = df

            time.sleep(REQUEST_DELAY)

        except Exception as e:
            logger.debug(f"  {symbol}/{report_name}/{period}: {e}")

    return results


def save_financial_data(symbol: str, data: dict, period: str):
    """Lưu báo cáo tài chính ra CSV."""
    symbol_dir = DATA_DIR / symbol
    symbol_dir.mkdir(parents=True, exist_ok=True)

    for report_name, df in data.items():
        # Xử lý MultiIndex columns (ratio có thể trả về MultiIndex)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(str(c) for c in col if str(c) != '').strip('_') for col in df.columns]

        filename = f"{report_name}_{period}.csv"
        filepath = symbol_dir / filename
        df.to_csv(filepath, index=False, encoding="utf-8-sig")

    return len(data)


# ============================================================
# MAIN COLLECTOR
# ============================================================

def collect_financials(symbols: list, periods: list):
    """Thu thập dữ liệu tài chính cho danh sách mã."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    total = len(symbols)
    success = 0
    errors = []

    for idx, symbol in enumerate(symbols):
        if (idx + 1) % 50 == 0 or idx == 0:
            logger.info(f"  [{idx + 1}/{total}] {symbol}... (OK: {success}, lỗi: {len(errors)})")

        symbol_ok = False
        for period in periods:
            try:
                data = fetch_financials(symbol, period=period)
                if data:
                    save_financial_data(symbol, data, period)
                    symbol_ok = True
            except Exception as e:
                logger.debug(f"  {symbol}/{period}: {e}")

        if symbol_ok:
            success += 1
        else:
            errors.append(symbol)

    logger.info(f"\nKết quả: {success}/{total} mã thành công, {len(errors)} lỗi")
    if errors:
        logger.warning(f"  Mã lỗi: {errors[:20]}{'...' if len(errors) > 20 else ''}")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Thu thập dữ liệu tài chính cho top N cổ phiếu vốn hóa lớn nhất.",
    )
    parser.add_argument("--top-n", type=int, default=500,
                        help="Số mã vốn hóa lớn nhất (mặc định: 500)")
    parser.add_argument("--period", type=str, default=None,
                        choices=["year", "quarter"],
                        help="Chỉ lấy 1 kỳ (mặc định: cả year + quarter)")
    args = parser.parse_args()

    periods = [args.period] if args.period else ["year", "quarter"]

    logger.info("=" * 60)
    logger.info("THU THẬP DỮ LIỆU TÀI CHÍNH")
    logger.info(f"Top: {args.top_n} vốn hóa lớn nhất")
    logger.info(f"Nguồn: VCI | Kỳ: {', '.join(periods)}")
    logger.info(f"Báo cáo: {', '.join(r[1] for r in REPORT_TYPES)}")
    logger.info(f"Output: {DATA_DIR}")
    logger.info("=" * 60)

    # 1. Lấy danh sách top N
    logger.info("\n[1/2] XÁC ĐỊNH TOP MÃ VỐN HÓA")
    symbols = get_top_symbols(top_n=args.top_n)

    if not symbols:
        logger.error("Không lấy được danh sách mã. Dừng lại.")
        return

    # 2. Fetch tài chính
    logger.info(f"\n[2/2] FETCH DỮ LIỆU TÀI CHÍNH ({len(symbols)} mã × {len(periods)} kỳ × {len(REPORT_TYPES)} báo cáo)")
    collect_financials(symbols, periods)

    logger.info("\n" + "=" * 60)
    logger.info("HOÀN TẤT!")
    logger.info(f"Dữ liệu: {DATA_DIR}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
