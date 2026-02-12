"""
Thu thập dữ liệu bổ sung hàng ngày: giá vàng, tỷ giá, thông tin công ty, sự kiện, giao dịch nội bộ.

Output:
    data/gold_prices.csv        - Giá vàng SJC (append hàng ngày)
    data/exchange_rates.csv     - Tỷ giá VCB (append hàng ngày)
    data/company_overview.csv   - Thông tin 500 công ty (PE/PB/ngành/vốn hóa, snapshot)
    data/company_ratios.csv     - Chỉ số tài chính (PE/PB/EPS/ROE, snapshot)
    data/company_events.csv     - Sự kiện công ty (cổ tức, ĐHCĐ, phát hành)
    data/insider_trading.csv    - Giao dịch nội bộ (snapshot)
    data/shareholders.csv       - Cổ đông lớn (snapshot)
    data/company_news.csv       - Tin tức công ty (VCI, snapshot)
    data/company_officers.csv   - Ban lãnh đạo (VCI, snapshot)
    data/subsidiaries.csv       - Công ty con (KBS, snapshot)

Cách chạy:
    python scripts/collect_extras.py                           # Tất cả
    python scripts/collect_extras.py --date 2026-02-11         # Ngày cụ thể
    python scripts/collect_extras.py --skip-company            # Bỏ qua company data
"""

import sys
import time
import logging
import argparse
import requests
import base64
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from utils import init_rate_limiter, get_limiter

# ============================================================
# CẤU HÌNH
# ============================================================

DATA_DIR = PROJECT_ROOT / "data"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("extras")

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

# Thread-safe rate limiter lock for vnstock API calls
_api_lock = threading.Lock()
MAX_WORKERS = 5  # Threads for company data (conservative: vnai allows 600/min)


def _rate_limited_call(func):
    """Call func with global rate limiter (thread-safe)."""
    with _api_lock:
        get_limiter().wait()
    return func()


# ============================================================
# 1. GIÁ VÀNG SJC
# ============================================================

def collect_gold_prices(date_str: str):
    """Thu thập giá vàng SJC cho ngày cụ thể, append vào CSV."""
    logger.info("Đang lấy giá vàng SJC...")

    csv_path = DATA_DIR / "gold_prices.csv"

    # Check if today's data already exists
    if csv_path.exists():
        existing = pd.read_csv(csv_path)
        if 'date' in existing.columns and date_str in existing['date'].values:
            logger.info(f"  Đã có dữ liệu ngày {date_str}, bỏ qua.")
            return True

    # Fetch from SJC API
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = dt.strftime("%d/%m/%Y")

        url = "https://sjc.com.vn/GoldPrice/Services/PriceService.ashx"
        payload = f"method=GetSJCGoldPriceByDate&toDate={formatted_date}"
        headers = {
            **_HEADERS,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }

        resp = requests.post(url, headers=headers, data=payload, timeout=30)
        if resp.status_code != 200:
            logger.warning(f"  SJC API lỗi: HTTP {resp.status_code}")
            return False

        data = resp.json()
        if not data.get("success") or not data.get("data"):
            logger.warning("  SJC: không có dữ liệu.")
            return False

        rows = []
        for item in data["data"]:
            rows.append({
                "date": date_str,
                "name": item.get("TypeName", ""),
                "branch": item.get("BranchName", ""),
                "buy_price": float(item.get("BuyValue", 0)),
                "sell_price": float(item.get("SellValue", 0)),
            })

        df = pd.DataFrame(rows)

        # Append to existing or create new
        if csv_path.exists():
            existing = pd.read_csv(csv_path)
            df = pd.concat([existing, df], ignore_index=True)
            df = df.drop_duplicates(subset=["date", "name", "branch"], keep="last")

        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        logger.info(f"  OK: {len(rows)} dòng giá vàng → {csv_path.name}")
        return True

    except Exception as e:
        logger.warning(f"  SJC lỗi: {e}")
        return False


# ============================================================
# 2. TỶ GIÁ VCB
# ============================================================

def collect_exchange_rates(date_str: str):
    """Thu thập tỷ giá VCB cho ngày cụ thể, append vào CSV."""
    logger.info("Đang lấy tỷ giá VCB...")

    csv_path = DATA_DIR / "exchange_rates.csv"

    # Check if today's data already exists
    if csv_path.exists():
        existing = pd.read_csv(csv_path)
        if 'date' in existing.columns and date_str in existing['date'].values:
            logger.info(f"  Đã có dữ liệu ngày {date_str}, bỏ qua.")
            return True

    try:
        url = f"https://www.vietcombank.com.vn/api/exchangerates/exportexcel?date={date_str}"
        resp = requests.get(url, headers=_HEADERS, timeout=30)
        if resp.status_code != 200:
            logger.warning(f"  VCB API lỗi: HTTP {resp.status_code}")
            return False

        json_data = resp.json()
        excel_data = base64.b64decode(json_data["Data"])
        df = pd.read_excel(BytesIO(excel_data), sheet_name='ExchangeRate')
        df.columns = ['currency_code', 'currency_name', 'buy_cash', 'buy_transfer', 'sell']
        df = df.iloc[2:-4]  # Remove header and footer rows
        df['date'] = date_str

        # Reorder columns
        df = df[['date', 'currency_code', 'currency_name', 'buy_cash', 'buy_transfer', 'sell']]

        # Append to existing or create new
        if csv_path.exists():
            existing = pd.read_csv(csv_path)
            df = pd.concat([existing, df], ignore_index=True)
            df = df.drop_duplicates(subset=["date", "currency_code"], keep="last")

        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        logger.info(f"  OK: {len(df[df['date'] == date_str])} loại tiền tệ → {csv_path.name}")
        return True

    except Exception as e:
        logger.warning(f"  VCB lỗi: {e}")
        return False


# ============================================================
# 3. COMPANY OVERVIEW (PE/PB/ngành/vốn hóa cho top 500)
# ============================================================

def _fetch_overview_one(symbol: str):
    """Fetch overview + ratio for one symbol (runs in thread)."""
    from vnstock.common.client import Vnstock
    result = {"overview": None, "ratios": None, "ok": False}
    try:
        client_s = Vnstock(source="VCI", show_log=False)
        stock_s = client_s.stock(symbol=symbol, source="VCI")

        try:
            ov = _rate_limited_call(lambda: stock_s.company.overview())
            if ov is not None and not ov.empty:
                result["overview"] = ov
        except Exception:
            pass

        try:
            rs = _rate_limited_call(lambda: stock_s.company.ratio_summary())
            if rs is not None and not rs.empty:
                result["ratios"] = rs
        except Exception:
            pass

        result["ok"] = True
    except Exception:
        pass
    return result


def collect_company_overview(top_n: int = 200):
    """
    Thu thập thông tin tổng quan công ty cho top N mã (song song).
    Lưu snapshot (overwrite mỗi ngày).
    """
    logger.info(f"Đang lấy company overview cho top {top_n} mã ({MAX_WORKERS} threads)...")

    from vnstock.common.client import Vnstock

    client = Vnstock(source="VCI", show_log=False)
    stock = client.stock(symbol="ACB", source="VCI")
    symbols_df = stock.listing.symbols_by_exchange(show_log=False)
    all_symbols = symbols_df["symbol"].tolist()[:top_n]

    all_overview = []
    all_ratios = []
    success = 0
    errors = 0
    completed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_fetch_overview_one, sym): sym for sym in all_symbols}
        for future in as_completed(futures):
            completed += 1
            if completed % 50 == 0 or completed == len(all_symbols):
                logger.info(f"  [{completed}/{top_n}] (OK: {success}, lỗi: {errors})")
            try:
                r = future.result()
                if r["ok"]:
                    success += 1
                    if r["overview"] is not None:
                        all_overview.append(r["overview"])
                    if r["ratios"] is not None:
                        all_ratios.append(r["ratios"])
                else:
                    errors += 1
            except Exception:
                errors += 1

    csv_overview = DATA_DIR / "company_overview.csv"
    if all_overview:
        df_overview = pd.concat(all_overview, ignore_index=True)
        df_overview.to_csv(csv_overview, index=False, encoding="utf-8-sig")
        logger.info(f"  Overview: {len(df_overview)} mã → {csv_overview.name}")

    csv_ratios = DATA_DIR / "company_ratios.csv"
    if all_ratios:
        df_ratios = pd.concat(all_ratios, ignore_index=True)
        df_ratios.to_csv(csv_ratios, index=False, encoding="utf-8-sig")
        logger.info(f"  Ratios: {len(df_ratios)} mã → {csv_ratios.name}")

    logger.info(f"  Kết quả: {success}/{top_n} mã, {errors} lỗi")
    return success > 0


# ============================================================
# GENERIC CONCURRENT COMPANY DATA FETCHER
# ============================================================

def _collect_company_data_concurrent(
    label: str,
    fetch_func,
    symbols: list,
    csv_path,
    add_symbol_col: bool = True,
):
    """
    Generic concurrent fetcher for company data.
    fetch_func(symbol) → DataFrame or None
    """
    top_n = len(symbols)
    logger.info(f"Đang lấy {label} cho {top_n} mã ({MAX_WORKERS} threads)...")

    all_data = []
    success = 0
    errors = 0
    completed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for sym in symbols:
            futures[executor.submit(fetch_func, sym)] = sym

        for future in as_completed(futures):
            completed += 1
            symbol = futures[future]
            if completed % 50 == 0 or completed == top_n:
                logger.info(f"  [{completed}/{top_n}] (OK: {success}, lỗi: {errors})")
            try:
                df = future.result()
                if df is not None and not df.empty:
                    if add_symbol_col:
                        df["symbol"] = symbol
                    all_data.append(df)
                success += 1
            except Exception:
                errors += 1

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        combined.to_csv(csv_path, index=False, encoding="utf-8-sig")
        logger.info(f"  {label}: {len(combined)} rows → {csv_path.name}")

    logger.info(f"  Kết quả: {success}/{top_n} mã, {errors} lỗi")
    return success > 0


def _get_symbols(source: str, top_n: int) -> list:
    """Get top N symbols from listing."""
    from vnstock.common.client import Vnstock
    client = Vnstock(source=source, show_log=False)
    stock = client.stock(symbol="ACB", source=source)
    symbols_df = stock.listing.symbols_by_exchange(show_log=False)
    return symbols_df["symbol"].tolist()[:top_n]


# ============================================================
# 4. COMPANY EVENTS (KBS)
# ============================================================

def collect_company_events(top_n: int = 50):
    symbols = _get_symbols("KBS", top_n)

    def fetch(symbol):
        from vnstock.explorer.kbs.company import Company
        comp = Company(symbol, show_log=False)
        return _rate_limited_call(lambda: comp.events(page_size=50))

    return _collect_company_data_concurrent(
        "Events", fetch, symbols, DATA_DIR / "company_events.csv"
    )


# ============================================================
# 5. INSIDER TRADING (KBS)
# ============================================================

def collect_insider_trading(top_n: int = 50):
    symbols = _get_symbols("KBS", top_n)

    def fetch(symbol):
        from vnstock.explorer.kbs.company import Company
        comp = Company(symbol, show_log=False)
        return _rate_limited_call(lambda: comp.insider_trading(page_size=20))

    return _collect_company_data_concurrent(
        "Insider", fetch, symbols, DATA_DIR / "insider_trading.csv"
    )


# ============================================================
# 6. SHAREHOLDERS (KBS)
# ============================================================

def collect_shareholders(top_n: int = 50):
    symbols = _get_symbols("KBS", top_n)

    def fetch(symbol):
        from vnstock.explorer.kbs.company import Company
        comp = Company(symbol, show_log=False)
        return _rate_limited_call(lambda: comp.shareholders())

    return _collect_company_data_concurrent(
        "Shareholders", fetch, symbols, DATA_DIR / "shareholders.csv"
    )


# ============================================================
# 7. COMPANY NEWS (VCI)
# ============================================================

def collect_company_news(top_n: int = 50):
    symbols = _get_symbols("VCI", top_n)

    def fetch(symbol):
        from vnstock.common.client import Vnstock
        client_s = Vnstock(source="VCI", show_log=False)
        stock_s = client_s.stock(symbol=symbol, source="VCI")
        return _rate_limited_call(lambda: stock_s.company.news())

    return _collect_company_data_concurrent(
        "News", fetch, symbols, DATA_DIR / "company_news.csv"
    )


# ============================================================
# 8. COMPANY OFFICERS (VCI)
# ============================================================

def collect_company_officers(top_n: int = 50):
    symbols = _get_symbols("VCI", top_n)

    def fetch(symbol):
        from vnstock.common.client import Vnstock
        client_s = Vnstock(source="VCI", show_log=False)
        stock_s = client_s.stock(symbol=symbol, source="VCI")
        return _rate_limited_call(lambda: stock_s.company.officers())

    return _collect_company_data_concurrent(
        "Officers", fetch, symbols, DATA_DIR / "company_officers.csv"
    )


# ============================================================
# 9. SUBSIDIARIES (KBS)
# ============================================================

def collect_subsidiaries(top_n: int = 50):
    symbols = _get_symbols("KBS", top_n)

    def fetch(symbol):
        from vnstock.explorer.kbs.company import Company
        comp = Company(symbol, show_log=False)
        return _rate_limited_call(lambda: comp.subsidiaries())

    return _collect_company_data_concurrent(
        "Subsidiaries", fetch, symbols, DATA_DIR / "subsidiaries.csv"
    )


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Thu thập dữ liệu bổ sung: giá vàng, tỷ giá, company overview, events, insider.",
    )
    parser.add_argument("--date", default=None,
                        help="Ngày thu thập (YYYY-MM-DD). Mặc định: hôm nay")
    parser.add_argument("--top-n", type=int, default=200,
                        help="Số mã cho company overview (mặc định: 200)")
    parser.add_argument("--top-n-events", type=int, default=50,
                        help="Số mã cho events/insider/shareholders (mặc định: 50)")
    parser.add_argument("--skip-company", action="store_true",
                        help="Bỏ qua tất cả company data")
    args = parser.parse_args()

    date_str = args.date or datetime.now().strftime("%Y-%m-%d")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize rate limiter (auto-detects tier from VNSTOCK_API_KEY)
    init_rate_limiter()

    total_steps = 2
    if not args.skip_company:
        total_steps += 7  # overview, events, insider, shareholders, news, officers, subsidiaries

    logger.info("=" * 60)
    logger.info("THU THẬP DỮ LIỆU BỔ SUNG")
    logger.info(f"Ngày: {date_str}")
    logger.info(f"Output: {DATA_DIR}")
    logger.info("=" * 60)

    step = 1

    # 1. Giá vàng
    logger.info(f"\n[{step}/{total_steps}] GIÁ VÀNG SJC")
    collect_gold_prices(date_str)
    step += 1

    # 2. Tỷ giá
    logger.info(f"\n[{step}/{total_steps}] TỶ GIÁ VCB")
    collect_exchange_rates(date_str)
    step += 1

    if not args.skip_company:
        # 3. Company overview
        logger.info(f"\n[{step}/{total_steps}] COMPANY OVERVIEW ({args.top_n} mã)")
        collect_company_overview(top_n=args.top_n)
        step += 1

        # 4. Company events
        logger.info(f"\n[{step}/{total_steps}] COMPANY EVENTS ({args.top_n_events} mã)")
        collect_company_events(top_n=args.top_n_events)
        step += 1

        # 5. Insider trading
        logger.info(f"\n[{step}/{total_steps}] INSIDER TRADING ({args.top_n_events} mã)")
        collect_insider_trading(top_n=args.top_n_events)
        step += 1

        # 6. Shareholders
        logger.info(f"\n[{step}/{total_steps}] SHAREHOLDERS ({args.top_n_events} mã)")
        collect_shareholders(top_n=args.top_n_events)
        step += 1

        # 7. Company news (VCI)
        logger.info(f"\n[{step}/{total_steps}] COMPANY NEWS ({args.top_n_events} mã)")
        collect_company_news(top_n=args.top_n_events)
        step += 1

        # 8. Company officers (VCI)
        logger.info(f"\n[{step}/{total_steps}] COMPANY OFFICERS ({args.top_n_events} mã)")
        collect_company_officers(top_n=args.top_n_events)
        step += 1

        # 9. Subsidiaries (KBS)
        logger.info(f"\n[{step}/{total_steps}] SUBSIDIARIES ({args.top_n_events} mã)")
        collect_subsidiaries(top_n=args.top_n_events)

    logger.info("\n" + "=" * 60)
    logger.info("HOÀN TẤT!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
