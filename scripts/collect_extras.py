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
from io import BytesIO
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

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

def collect_company_overview(top_n: int = 500):
    """
    Thu thập thông tin tổng quan công ty cho top N mã.
    Lưu snapshot (overwrite mỗi ngày).
    """
    logger.info(f"Đang lấy company overview cho top {top_n} mã...")

    from vnstock.common.client import Vnstock

    # Get top symbols (reuse logic from collect_stocks.py)
    client = Vnstock(source="VCI", show_log=False)
    stock = client.stock(symbol="ACB", source="VCI")
    symbols_df = stock.listing.symbols_by_exchange(show_log=False)
    all_symbols = symbols_df["symbol"].tolist()[:top_n]

    all_overview = []
    all_ratios = []
    success = 0
    errors = 0

    for idx, symbol in enumerate(all_symbols):
        if (idx + 1) % 50 == 0 or idx == 0:
            logger.info(f"  [{idx + 1}/{top_n}] {symbol}... (OK: {success}, lỗi: {errors})")

        try:
            client_s = Vnstock(source="VCI", show_log=False)
            stock_s = client_s.stock(symbol=symbol, source="VCI")

            # Company overview
            try:
                ov = stock_s.company.overview()
                if ov is not None and not ov.empty:
                    all_overview.append(ov)
            except Exception:
                pass

            # Ratio summary (PE, PB, EPS, ROE, etc.)
            try:
                rs = stock_s.company.ratio_summary()
                if rs is not None and not rs.empty:
                    all_ratios.append(rs)
            except Exception:
                pass

            success += 1
            time.sleep(0.05)

        except Exception:
            errors += 1

    # Save overview
    csv_overview = DATA_DIR / "company_overview.csv"
    if all_overview:
        df_overview = pd.concat(all_overview, ignore_index=True)
        df_overview.to_csv(csv_overview, index=False, encoding="utf-8-sig")
        logger.info(f"  Overview: {len(df_overview)} mã → {csv_overview.name}")

    # Save ratio summary
    csv_ratios = DATA_DIR / "company_ratios.csv"
    if all_ratios:
        df_ratios = pd.concat(all_ratios, ignore_index=True)
        df_ratios.to_csv(csv_ratios, index=False, encoding="utf-8-sig")
        logger.info(f"  Ratios: {len(df_ratios)} mã → {csv_ratios.name}")

    logger.info(f"  Kết quả: {success}/{top_n} mã, {errors} lỗi")
    return success > 0


# ============================================================
# 4. COMPANY EVENTS (KBS - Cổ tức, ĐHCĐ, Phát hành)
# ============================================================

def collect_company_events(top_n: int = 100):
    """
    Thu thập sự kiện công ty (cổ tức, ĐHCĐ, phát hành, giao dịch nội bộ) cho top N mã.
    Snapshot overwrite mỗi ngày.
    """
    logger.info(f"Đang lấy company events cho top {top_n} mã...")

    from vnstock.common.client import Vnstock

    client = Vnstock(source="KBS", show_log=False)
    stock = client.stock(symbol="ACB", source="KBS")
    symbols_df = stock.listing.symbols_by_exchange(show_log=False)
    all_symbols = symbols_df["symbol"].tolist()[:top_n]

    all_events = []
    success = 0
    errors = 0

    for idx, symbol in enumerate(all_symbols):
        if (idx + 1) % 50 == 0 or idx == 0:
            logger.info(f"  [{idx + 1}/{top_n}] {symbol}... (OK: {success}, lỗi: {errors})")

        try:
            from vnstock.explorer.kbs.company import Company
            comp = Company(symbol, show_log=False)

            # Get all event types (page_size=50 to get recent events)
            try:
                ev = comp.events(page_size=50)
                if ev is not None and not ev.empty:
                    ev["symbol"] = symbol
                    all_events.append(ev)
            except Exception:
                pass

            success += 1
            time.sleep(0.05)

        except Exception:
            errors += 1

    csv_events = DATA_DIR / "company_events.csv"
    if all_events:
        df_events = pd.concat(all_events, ignore_index=True)
        df_events.to_csv(csv_events, index=False, encoding="utf-8-sig")
        logger.info(f"  Events: {len(df_events)} sự kiện → {csv_events.name}")

    logger.info(f"  Kết quả: {success}/{top_n} mã, {errors} lỗi")
    return success > 0


# ============================================================
# 5. INSIDER TRADING (KBS)
# ============================================================

def collect_insider_trading(top_n: int = 100):
    """
    Thu thập giao dịch nội bộ cho top N mã.
    Snapshot overwrite mỗi ngày.
    """
    logger.info(f"Đang lấy insider trading cho top {top_n} mã...")

    from vnstock.common.client import Vnstock

    client = Vnstock(source="KBS", show_log=False)
    stock = client.stock(symbol="ACB", source="KBS")
    symbols_df = stock.listing.symbols_by_exchange(show_log=False)
    all_symbols = symbols_df["symbol"].tolist()[:top_n]

    all_insider = []
    success = 0
    errors = 0

    for idx, symbol in enumerate(all_symbols):
        if (idx + 1) % 50 == 0 or idx == 0:
            logger.info(f"  [{idx + 1}/{top_n}] {symbol}... (OK: {success}, lỗi: {errors})")

        try:
            from vnstock.explorer.kbs.company import Company
            comp = Company(symbol, show_log=False)

            try:
                ins = comp.insider_trading(page_size=20)
                if ins is not None and not ins.empty:
                    ins["symbol"] = symbol
                    all_insider.append(ins)
            except Exception:
                pass

            success += 1
            time.sleep(0.05)

        except Exception:
            errors += 1

    csv_insider = DATA_DIR / "insider_trading.csv"
    if all_insider:
        df_insider = pd.concat(all_insider, ignore_index=True)
        df_insider.to_csv(csv_insider, index=False, encoding="utf-8-sig")
        logger.info(f"  Insider: {len(df_insider)} giao dịch → {csv_insider.name}")

    logger.info(f"  Kết quả: {success}/{top_n} mã, {errors} lỗi")
    return success > 0


# ============================================================
# 6. SHAREHOLDERS (KBS)
# ============================================================

def collect_shareholders(top_n: int = 100):
    """
    Thu thập thông tin cổ đông lớn cho top N mã.
    Snapshot overwrite mỗi ngày.
    """
    logger.info(f"Đang lấy shareholders cho top {top_n} mã...")

    from vnstock.common.client import Vnstock

    client = Vnstock(source="KBS", show_log=False)
    stock = client.stock(symbol="ACB", source="KBS")
    symbols_df = stock.listing.symbols_by_exchange(show_log=False)
    all_symbols = symbols_df["symbol"].tolist()[:top_n]

    all_shareholders = []
    success = 0
    errors = 0

    for idx, symbol in enumerate(all_symbols):
        if (idx + 1) % 50 == 0 or idx == 0:
            logger.info(f"  [{idx + 1}/{top_n}] {symbol}... (OK: {success}, lỗi: {errors})")

        try:
            from vnstock.explorer.kbs.company import Company
            comp = Company(symbol, show_log=False)

            try:
                sh = comp.shareholders()
                if sh is not None and not sh.empty:
                    sh["symbol"] = symbol
                    all_shareholders.append(sh)
            except Exception:
                pass

            success += 1
            time.sleep(0.05)

        except Exception:
            errors += 1

    csv_shareholders = DATA_DIR / "shareholders.csv"
    if all_shareholders:
        df_sh = pd.concat(all_shareholders, ignore_index=True)
        df_sh.to_csv(csv_shareholders, index=False, encoding="utf-8-sig")
        logger.info(f"  Shareholders: {len(df_sh)} cổ đông → {csv_shareholders.name}")

    logger.info(f"  Kết quả: {success}/{top_n} mã, {errors} lỗi")
    return success > 0


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Thu thập dữ liệu bổ sung: giá vàng, tỷ giá, company overview, events, insider.",
    )
    parser.add_argument("--date", default=None,
                        help="Ngày thu thập (YYYY-MM-DD). Mặc định: hôm nay")
    parser.add_argument("--top-n", type=int, default=500,
                        help="Số mã cho company overview (mặc định: 500)")
    parser.add_argument("--top-n-events", type=int, default=100,
                        help="Số mã cho events/insider/shareholders (mặc định: 100)")
    parser.add_argument("--skip-company", action="store_true",
                        help="Bỏ qua tất cả company data")
    args = parser.parse_args()

    date_str = args.date or datetime.now().strftime("%Y-%m-%d")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    total_steps = 2
    if not args.skip_company:
        total_steps += 4  # overview, events, insider, shareholders

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

    logger.info("\n" + "=" * 60)
    logger.info("HOÀN TẤT!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
