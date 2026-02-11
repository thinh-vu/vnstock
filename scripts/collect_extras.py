"""
Thu thập dữ liệu bổ sung hàng ngày: giá vàng, tỷ giá, thông tin công ty.

Output:
    data/gold_prices.csv        - Giá vàng SJC (append hàng ngày)
    data/exchange_rates.csv     - Tỷ giá VCB (append hàng ngày)
    data/company_overview.csv   - Thông tin 500 công ty (PE/PB/ngành/vốn hóa, snapshot)

Cách chạy:
    python scripts/collect_extras.py                           # Tất cả
    python scripts/collect_extras.py --date 2026-02-11         # Ngày cụ thể
    python scripts/collect_extras.py --skip-company            # Bỏ qua company overview
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
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Thu thập dữ liệu bổ sung: giá vàng, tỷ giá, company overview.",
    )
    parser.add_argument("--date", default=None,
                        help="Ngày thu thập (YYYY-MM-DD). Mặc định: hôm nay")
    parser.add_argument("--top-n", type=int, default=500,
                        help="Số mã cho company overview (mặc định: 500)")
    parser.add_argument("--skip-company", action="store_true",
                        help="Bỏ qua company overview (chỉ lấy vàng + tỷ giá)")
    args = parser.parse_args()

    date_str = args.date or datetime.now().strftime("%Y-%m-%d")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("THU THẬP DỮ LIỆU BỔ SUNG")
    logger.info(f"Ngày: {date_str}")
    logger.info(f"Output: {DATA_DIR}")
    logger.info("=" * 60)

    step = 1
    total_steps = 2 if args.skip_company else 3

    # 1. Giá vàng
    logger.info(f"\n[{step}/{total_steps}] GIÁ VÀNG SJC")
    collect_gold_prices(date_str)
    step += 1

    # 2. Tỷ giá
    logger.info(f"\n[{step}/{total_steps}] TỶ GIÁ VCB")
    collect_exchange_rates(date_str)
    step += 1

    # 3. Company overview
    if not args.skip_company:
        logger.info(f"\n[{step}/{total_steps}] COMPANY OVERVIEW ({args.top_n} mã)")
        collect_company_overview(top_n=args.top_n)

    logger.info("\n" + "=" * 60)
    logger.info("HOÀN TẤT!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
