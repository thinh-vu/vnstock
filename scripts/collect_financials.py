"""
Thu thập dữ liệu tài chính cho top 500 cổ phiếu vốn hóa lớn nhất.

Nguồn: KBS SAS Finance API (REST, ổn định, không cần auth).
Dữ liệu chỉ thay đổi theo quý → chạy khi cần.

Output:
    data/financials/
    ├── VCB/
    │   ├── balance_sheet_year.csv
    │   ├── balance_sheet_quarter.csv
    │   ├── income_statement_year.csv
    │   ├── income_statement_quarter.csv
    │   ├── cash_flow_year.csv
    │   ├── cash_flow_quarter.csv
    │   ├── ratio_year.csv
    │   └── ratio_quarter.csv
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
import requests
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

# KBS SAS Finance API (same domain as price_board - works on GitHub Actions)
_KBS_FINANCE_URL = "https://kbbuddywts.kbsec.com.vn/sas/kbsv-stock-data-store/stock/finance-info"
_KBS_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("financials")

# Các loại báo cáo cần lấy: (report_name, kbs_type, content_key)
REPORT_TYPES = [
    ("balance_sheet", "CDKT", "Cân đối kế toán"),
    ("income_statement", "KQKD", "Kết quả kinh doanh"),
    ("cash_flow", "LCTT", None),  # Cash flow key varies (gián tiếp/trực tiếp)
    ("ratio", "CSTC", None),  # Ratios have multiple groups
]


# ============================================================
# LẤY TOP N VỐN HÓA
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

    # Convert numeric columns
    for col in ['close_price', 'reference_price', 'listed_shares', 'total_listed_qty']:
        if col in board.columns:
            board[col] = pd.to_numeric(board[col], errors='coerce')

    # Determine price: use close_price, fallback to reference_price if close=0
    # (close_price = 0 ngoài giờ giao dịch, reference_price luôn có giá trị)
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

    # Determine shares column
    shares_col = None
    for col in ['total_listed_qty', 'listed_shares']:
        if col in board.columns and board[col].sum() > 0:
            shares_col = col
            break

    if shares_col:
        board['market_cap'] = board['price'] * board[shares_col]
        logger.info(f"Market cap: price * {shares_col}")
        sample = board[board['market_cap'] > 0].nlargest(3, 'market_cap')
        if not sample.empty:
            logger.info(f"  Top 3: {sample[['symbol', 'price', shares_col, 'market_cap']].to_dict('records')}")
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
        logger.warning(f"Market cap = 0 cho tất cả mã, dùng thứ tự mặc định (top {top_n}).")
        return all_symbols[:top_n]

    top = board.nlargest(top_n, 'market_cap')
    symbols = top['symbol'].tolist()
    logger.info(f"Top {top_n} vốn hóa: {len(symbols)} mã")
    return symbols


# ============================================================
# FETCH DỮ LIỆU TÀI CHÍNH TỪ KBS (Direct REST API)
# ============================================================

def _parse_kbs_response(json_data: dict, report_name: str) -> pd.DataFrame:
    """
    Parse KBS financial API response thành DataFrame.

    Returns:
        DataFrame với columns: item, item_en, + period columns (2024, 2023, ...)
    """
    if not json_data:
        return pd.DataFrame()

    head_list = json_data.get('Head', [])
    content = json_data.get('Content', {})

    # Extract period labels from Head
    periods = []
    if head_list:
        for head in head_list:
            if isinstance(head, dict):
                year = head.get('YearPeriod', '')
                term_name = head.get('TermName', '')
                if term_name and 'Quý' in term_name:
                    quarter_num = term_name.replace('Quý', '').strip()
                    periods.append(f"{year}-Q{quarter_num}")
                else:
                    periods.append(str(year))

    # Determine content key
    if report_name == "cash_flow":
        # Cash flow có 2 loại: gián tiếp (phổ biến) và trực tiếp
        report_data = (
            content.get('Lưu chuyển tiền tệ gián tiếp', [])
            or content.get('Lưu chuyển tiền tệ trực tiếp', [])
        )
    elif report_name == "ratio":
        # Ratios có nhiều nhóm, gộp lại
        report_data = []
        ratio_groups = [
            'Nhóm chỉ số Định giá',
            'Nhóm chỉ số Sinh lợi',
            'Nhóm chỉ số Tăng trưởng',
            'Nhóm chỉ số Thanh khoản',
            'Nhóm chỉ số Chất lượng tài sản',
        ]
        for group_key in ratio_groups:
            report_data.extend(content.get(group_key, []))
    elif report_name == "balance_sheet":
        report_data = content.get('Cân đối kế toán', [])
    elif report_name == "income_statement":
        report_data = content.get('Kết quả kinh doanh', [])
    else:
        return pd.DataFrame()

    if not report_data:
        return pd.DataFrame()

    # Build rows
    rows = []
    for record in report_data:
        row = {
            'item': record.get('Name', ''),
            'item_en': record.get('NameEn', ''),
        }
        for i, period_label in enumerate(periods, 1):
            value = record.get(f'Value{i}')
            if value is not None:
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    pass
            row[period_label] = value
        rows.append(row)

    return pd.DataFrame(rows)


def fetch_financials(symbol: str, period: str = 'year') -> dict:
    """
    Lấy toàn bộ báo cáo tài chính cho 1 mã từ KBS REST API.

    Returns:
        dict {report_name: DataFrame}
    """
    results = {}
    period_type = 1 if period == 'year' else 2

    for report_name, kbs_type, _ in REPORT_TYPES:
        try:
            url = f"{_KBS_FINANCE_URL}/{symbol}"
            params = {
                'page': 1,
                'pageSize': 20,  # Lấy 20 kỳ (nhiều hơn mặc định 8)
                'type': kbs_type,
                'unit': 1000,
                'termtype': period_type,
            }
            # Cash flow uses different param names
            if kbs_type == 'LCTT':
                params['code'] = symbol
                params['termType'] = period_type
            else:
                params['languageid'] = 1

            resp = requests.get(url, params=params, headers=_KBS_HEADERS, timeout=30)
            if resp.status_code != 200:
                logger.debug(f"  {symbol}/{report_name}: HTTP {resp.status_code}")
                continue

            json_data = resp.json()
            df = _parse_kbs_response(json_data, report_name)

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
    logger.info(f"Nguồn: KBS SAS Finance API | Kỳ: {', '.join(periods)}")
    logger.info(f"Báo cáo: {', '.join(r[0] for r in REPORT_TYPES)}")
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
