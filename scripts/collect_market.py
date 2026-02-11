"""
Thu thập dữ liệu thị trường bổ sung: FX, Crypto, World Indices, Fund, Listing metadata.

Output:
    data/fx/USDVND.csv          - Tỷ giá FX OHLCV (MSN)
    data/crypto/BTC.csv         - Crypto OHLCV (MSN)
    data/world_indices/DJI.csv  - Chỉ số thế giới OHLCV (MSN)
    data/funds/fund_listing.csv - Danh sách quỹ mở (FMARKET)
    data/funds/fund_nav.csv     - NAV lịch sử các quỹ (FMARKET)
    data/listing_metadata.csv   - Bonds, warrants, futures, industries (KBS)

Cách chạy:
    python scripts/collect_market.py                     # Tất cả
    python scripts/collect_market.py --only fx           # Chỉ FX
    python scripts/collect_market.py --only crypto       # Chỉ Crypto
    python scripts/collect_market.py --only world        # Chỉ World Indices
    python scripts/collect_market.py --only fund         # Chỉ Fund
    python scripts/collect_market.py --only listing      # Chỉ Listing metadata
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

import pandas as pd

# ============================================================
# CẤU HÌNH
# ============================================================

DATA_DIR = PROJECT_ROOT / "data"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("market")

# FX pairs to collect (from MSN const)
FX_PAIRS = [
    "USDVND", "EURUSD", "USDJPY", "GBPUSD", "AUDUSD",
    "USDCAD", "USDCHF", "USDCNY", "USDKRW", "USDSGD",
    "EURJPY", "EURGBP", "GBPJPY", "NZDUSD", "JPYVND",
]

# Crypto symbols
CRYPTO_SYMBOLS = ["BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE"]

# World indices
WORLD_INDICES = {
    "DJI": "Dow Jones",
    "INX": "S&P 500",
    "COMP": "Nasdaq",
    "N225": "Nikkei 225",
    "HSI": "Hang Seng",
    "DAX": "DAX",
    "UKX": "FTSE 100",
    "PX1": "CAC 40",
    "SENSEX": "BSE Sensex",
    "000001": "Shanghai",
    "RUT": "Russell 2000",
}


# ============================================================
# MSN API KEY (fetch once, reuse for all MSN calls)
# ============================================================

_msn_apikey_cache = None


def get_msn_apikey():
    """Lấy MSN API key với retry logic. Cache kết quả."""
    global _msn_apikey_cache
    if _msn_apikey_cache is not None:
        return _msn_apikey_cache

    from vnstock.core.utils.user_agent import get_headers
    headers = get_headers(data_source='MSN', random_agent=False)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"  Đang lấy MSN API key (lần {attempt}/{MAX_RETRIES})...")
            from vnstock.explorer.msn.helper import msn_apikey
            key = msn_apikey(headers=headers, version='20240430')
            _msn_apikey_cache = key
            logger.info("  MSN API key: OK")
            return key
        except Exception as e:
            logger.warning(f"  MSN API key lần {attempt} lỗi: {e}")
            if attempt < MAX_RETRIES:
                wait = RETRY_DELAY * attempt
                logger.info(f"  Chờ {wait}s rồi thử lại...")
                time.sleep(wait)

    logger.error("  MSN API key: THẤT BẠI sau 3 lần thử. Bỏ qua FX/Crypto/World.")
    return None


def msn_fetch_history(symbol_id: str, start: str, end: str, asset_type: str = "currency"):
    """Fetch OHLCV trực tiếp từ MSN API, dùng API key đã cache."""
    apikey = get_msn_apikey()
    if apikey is None:
        return None

    from vnstock.core.utils.user_agent import get_headers
    headers = get_headers(data_source='MSN', random_agent=False)

    if asset_type == "crypto":
        url = "https://assets.msn.com/service/Finance/Cryptocurrency/chart"
    else:
        url = "https://assets.msn.com/service/Finance/Charts/TimeRange"

    params = {
        "apikey": apikey,
        'StartTime': f'{start}T17:00:00.000Z',
        'EndTime': f'{end}T16:59:00.858Z',
        'timeframe': 1,
        "ocid": "finance-utils-peregrine",
        "cm": "vi-vn",
        "it": "web",
        "scn": "ANON",
        "ids": symbol_id.lower(),
        "type": "All",
        "wrapodata": "false",
        "disableSymbol": "false",
    }

    resp = requests.get(url, headers=headers, params=params, timeout=30)
    if resp.status_code != 200:
        raise ConnectionError(f"MSN HTTP {resp.status_code}")

    json_data = resp.json()[0]['series']

    # Convert to DataFrame
    df = pd.DataFrame(json_data)
    col_map = {
        'timeStamps': 'time', 'openPrices': 'open',
        'pricesHigh': 'high', 'pricesLow': 'low',
        'prices': 'close', 'volumes': 'volume',
    }
    df.rename(columns=col_map, inplace=True)
    drop_cols = [c for c in ['priceHigh', 'priceLow', 'startTime', 'endTime'] if c in df.columns]
    if drop_cols:
        df.drop(columns=drop_cols, inplace=True)

    df["time"] = pd.to_datetime(df["time"], errors='coerce')
    df['time'] = df['time'] + pd.Timedelta(hours=7)
    df['time'] = df['time'].dt.floor('D')
    for col in ["open", "high", "low", "close"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').round(2)
    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors='coerce').fillna(0).astype(int)

    keep_cols = [c for c in ['time', 'open', 'high', 'low', 'close', 'volume'] if c in df.columns]
    df = df[keep_cols]

    # Filter by date range
    df = df[(df['time'] >= start) & (df['time'] <= end)]
    df = df.replace(-99999901.0, None).dropna(subset=['open', 'high', 'low'])

    if asset_type == "currency" and "volume" in df.columns:
        df.drop(columns=['volume'], inplace=True)

    return df


# ============================================================
# INCREMENTAL MERGE HELPER
# ============================================================

def incremental_merge(csv_path, new_df, date_col="time"):
    """Merge new data with existing CSV file."""
    if csv_path.exists():
        try:
            existing = pd.read_csv(csv_path, parse_dates=[date_col])
            if not existing.empty:
                combined = pd.concat([existing, new_df])
                combined = (
                    combined.drop_duplicates(date_col, keep="last")
                    .sort_values(date_col).reset_index(drop=True)
                )
                return combined
        except Exception:
            pass
    return new_df.sort_values(date_col).reset_index(drop=True)


# ============================================================
# 1. FX RATES (MSN)
# ============================================================

def collect_fx(start: str, end: str):
    """Thu thập tỷ giá FX OHLCV từ MSN."""
    logger.info("Đang lấy tỷ giá FX từ MSN...")

    # Test MSN API key first
    if get_msn_apikey() is None:
        logger.warning("  MSN không khả dụng, bỏ qua FX.")
        return False

    from vnstock.explorer.msn.const import _CURRENCY_ID_MAP

    fx_dir = DATA_DIR / "fx"
    fx_dir.mkdir(parents=True, exist_ok=True)

    success = 0
    errors = []

    for pair in FX_PAIRS:
        csv_path = fx_dir / f"{pair}.csv"
        symbol_id = _CURRENCY_ID_MAP.get(pair)
        if not symbol_id:
            errors.append(pair)
            continue

        # Incremental: determine fetch start
        fetch_start = start
        if csv_path.exists():
            try:
                existing = pd.read_csv(csv_path, parse_dates=["time"])
                if not existing.empty:
                    fetch_start = (existing["time"].max() - timedelta(days=3)).strftime("%Y-%m-%d")
            except Exception:
                pass

        try:
            df = msn_fetch_history(symbol_id, fetch_start, end, asset_type="currency")
            if df is not None and not df.empty:
                df["symbol"] = pair
                combined = incremental_merge(csv_path, df)
                combined.to_csv(csv_path, index=False, encoding="utf-8-sig")
                success += 1
                logger.info(f"  {pair}: {len(combined)} rows")
            else:
                errors.append(pair)
        except Exception as e:
            errors.append(pair)
            logger.warning(f"  {pair}: lỗi - {e}")

        time.sleep(0.3)

    logger.info(f"  FX: {success}/{len(FX_PAIRS)} OK, lỗi: {errors}")
    return success > 0


# ============================================================
# 2. CRYPTO (MSN)
# ============================================================

def collect_crypto(start: str, end: str):
    """Thu thập giá crypto OHLCV từ MSN."""
    logger.info("Đang lấy giá crypto từ MSN...")

    if get_msn_apikey() is None:
        logger.warning("  MSN không khả dụng, bỏ qua Crypto.")
        return False

    from vnstock.explorer.msn.const import _CRYPTO_ID_MAP

    crypto_dir = DATA_DIR / "crypto"
    crypto_dir.mkdir(parents=True, exist_ok=True)

    success = 0
    errors = []

    for symbol in CRYPTO_SYMBOLS:
        csv_path = crypto_dir / f"{symbol}.csv"
        symbol_id = _CRYPTO_ID_MAP.get(symbol)
        if not symbol_id:
            errors.append(symbol)
            continue

        fetch_start = start
        if csv_path.exists():
            try:
                existing = pd.read_csv(csv_path, parse_dates=["time"])
                if not existing.empty:
                    fetch_start = (existing["time"].max() - timedelta(days=3)).strftime("%Y-%m-%d")
            except Exception:
                pass

        try:
            df = msn_fetch_history(symbol_id, fetch_start, end, asset_type="crypto")
            if df is not None and not df.empty:
                df["symbol"] = symbol
                combined = incremental_merge(csv_path, df)
                combined.to_csv(csv_path, index=False, encoding="utf-8-sig")
                success += 1
                logger.info(f"  {symbol}: {len(combined)} rows")
            else:
                errors.append(symbol)
        except Exception as e:
            errors.append(symbol)
            logger.warning(f"  {symbol}: lỗi - {e}")

        time.sleep(0.3)

    logger.info(f"  Crypto: {success}/{len(CRYPTO_SYMBOLS)} OK, lỗi: {errors}")
    return success > 0


# ============================================================
# 3. WORLD INDICES (MSN)
# ============================================================

def collect_world_indices(start: str, end: str):
    """Thu thập chỉ số thế giới OHLCV từ MSN."""
    logger.info("Đang lấy chỉ số thế giới từ MSN...")

    if get_msn_apikey() is None:
        logger.warning("  MSN không khả dụng, bỏ qua World Indices.")
        return False

    from vnstock.explorer.msn.const import _GLOBAL_INDICES

    idx_dir = DATA_DIR / "world_indices"
    idx_dir.mkdir(parents=True, exist_ok=True)

    success = 0
    errors = []

    for symbol, name in WORLD_INDICES.items():
        csv_path = idx_dir / f"{symbol}.csv"
        symbol_id = _GLOBAL_INDICES.get(symbol)
        if not symbol_id:
            errors.append(symbol)
            continue

        fetch_start = start
        if csv_path.exists():
            try:
                existing = pd.read_csv(csv_path, parse_dates=["time"])
                if not existing.empty:
                    fetch_start = (existing["time"].max() - timedelta(days=3)).strftime("%Y-%m-%d")
            except Exception:
                pass

        try:
            df = msn_fetch_history(symbol_id, fetch_start, end, asset_type="index")
            if df is not None and not df.empty:
                df["symbol"] = symbol
                df["name"] = name
                combined = incremental_merge(csv_path, df)
                combined.to_csv(csv_path, index=False, encoding="utf-8-sig")
                success += 1
                logger.info(f"  {symbol} ({name}): {len(combined)} rows")
            else:
                errors.append(symbol)
        except Exception as e:
            errors.append(symbol)
            logger.warning(f"  {symbol}: lỗi - {e}")

        time.sleep(0.3)

    logger.info(f"  World: {success}/{len(WORLD_INDICES)} OK, lỗi: {errors}")
    return success > 0


# ============================================================
# 4. FUND DATA (FMARKET)
# ============================================================

def collect_fund_data():
    """Thu thập danh sách quỹ mở + NAV từ FMARKET."""
    logger.info("Đang lấy dữ liệu quỹ mở từ FMARKET...")
    from vnstock.common.client import Vnstock

    fund_dir = DATA_DIR / "funds"
    fund_dir.mkdir(parents=True, exist_ok=True)

    success = 0

    try:
        client = Vnstock(show_log=False)
        fund = client.fund(source="FMARKET")

        # 1. Fund listing
        logger.info("  Lấy danh sách quỹ mở...")
        listing_df = fund.listing()
        if listing_df is not None and not listing_df.empty:
            listing_path = fund_dir / "fund_listing.csv"
            listing_df.to_csv(listing_path, index=False, encoding="utf-8-sig")
            logger.info(f"  Listing: {len(listing_df)} quỹ → {listing_path.name}")
            success += 1

            # 2. NAV report for each fund
            logger.info("  Lấy NAV lịch sử cho từng quỹ...")
            all_navs = []
            fund_names = listing_df["short_name"].tolist() if "short_name" in listing_df.columns else []

            for idx, fname in enumerate(fund_names):
                if (idx + 1) % 10 == 0:
                    logger.info(f"    [{idx + 1}/{len(fund_names)}] {fname}...")
                try:
                    nav_df = fund.details.nav_report(symbol=fname)
                    if nav_df is not None and not nav_df.empty:
                        nav_df["fund"] = fname
                        all_navs.append(nav_df)
                except Exception:
                    pass
                time.sleep(0.2)

            if all_navs:
                nav_combined = pd.concat(all_navs, ignore_index=True)
                nav_path = fund_dir / "fund_nav.csv"
                nav_combined.to_csv(nav_path, index=False, encoding="utf-8-sig")
                logger.info(f"  NAV: {len(nav_combined)} rows ({len(all_navs)} quỹ) → {nav_path.name}")
                success += 1

            # 3. Top holdings for each fund
            logger.info("  Lấy top holdings cho từng quỹ...")
            all_holdings = []

            for idx, fname in enumerate(fund_names):
                if (idx + 1) % 10 == 0:
                    logger.info(f"    [{idx + 1}/{len(fund_names)}] {fname}...")
                try:
                    hold_df = fund.details.top_holding(symbol=fname)
                    if hold_df is not None and not hold_df.empty:
                        all_holdings.append(hold_df)
                except Exception:
                    pass
                time.sleep(0.2)

            if all_holdings:
                hold_combined = pd.concat(all_holdings, ignore_index=True)
                hold_path = fund_dir / "fund_holdings.csv"
                hold_combined.to_csv(hold_path, index=False, encoding="utf-8-sig")
                logger.info(f"  Holdings: {len(hold_combined)} rows → {hold_path.name}")
                success += 1

    except Exception as e:
        logger.warning(f"  Fund lỗi: {e}")

    return success > 0


# ============================================================
# 5. LISTING METADATA (KBS)
# ============================================================

def collect_listing_metadata():
    """Thu thập metadata: industries, bonds, warrants, futures."""
    logger.info("Đang lấy listing metadata từ KBS...")
    from vnstock.common.client import Vnstock

    meta_dir = DATA_DIR / "metadata"
    meta_dir.mkdir(parents=True, exist_ok=True)

    success = 0

    try:
        client = Vnstock(source="KBS", show_log=False)
        stock = client.stock(symbol="ACB", source="KBS")

        items = [
            ("industries_icb", "Phân ngành ICB", "industries_icb.csv"),
            ("symbols_by_industries", "Mã theo ngành", "symbols_by_industry.csv"),
            ("all_future_indices", "Hợp đồng tương lai", "futures.csv"),
            ("all_covered_warrant", "Chứng quyền", "covered_warrants.csv"),
            ("all_bonds", "Trái phiếu DN", "corporate_bonds.csv"),
            ("all_government_bonds", "Trái phiếu CP", "government_bonds.csv"),
        ]

        for method_name, label, filename in items:
            try:
                logger.info(f"  Lấy {label}...")
                method = getattr(stock.listing, method_name)
                df = method()
                if df is not None and not df.empty:
                    df.to_csv(meta_dir / filename, index=False, encoding="utf-8-sig")
                    logger.info(f"  {label}: {len(df)} rows")
                    success += 1
            except Exception as e:
                logger.warning(f"  {label} lỗi: {e}")

    except Exception as e:
        logger.warning(f"  Listing metadata lỗi: {e}")

    return success > 0


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Thu thập dữ liệu thị trường: FX, Crypto, World Indices, Fund, Listing.",
    )
    parser.add_argument("--start", default=None,
                        help="Ngày bắt đầu (YYYY-MM-DD). Mặc định: 1 năm trước")
    parser.add_argument("--end", default=None,
                        help="Ngày kết thúc (YYYY-MM-DD). Mặc định: hôm nay")
    parser.add_argument("--only", default=None,
                        choices=["fx", "crypto", "world", "fund", "listing"],
                        help="Chỉ chạy 1 phần cụ thể")
    args = parser.parse_args()

    end = args.end or datetime.now().strftime("%Y-%m-%d")
    start = args.start or (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Run Fund + Listing first (independent of MSN)
    # Then MSN-dependent sections (FX, Crypto, World)
    sections = {
        "fund": ("FUND DATA (FMARKET)", collect_fund_data),
        "listing": ("LISTING METADATA (KBS)", collect_listing_metadata),
        "fx": ("FX RATES (MSN)", lambda: collect_fx(start, end)),
        "crypto": ("CRYPTO (MSN)", lambda: collect_crypto(start, end)),
        "world": ("WORLD INDICES (MSN)", lambda: collect_world_indices(start, end)),
    }

    if args.only:
        sections = {args.only: sections[args.only]}

    logger.info("=" * 60)
    logger.info("THU THẬP DỮ LIỆU THỊ TRƯỜNG BỔ SUNG")
    logger.info(f"Thời gian: {start} -> {end}")
    logger.info(f"Sections: {list(sections.keys())}")
    logger.info(f"Output: {DATA_DIR}")
    logger.info("=" * 60)

    step = 0
    total = len(sections)

    for key, (title, func) in sections.items():
        step += 1
        logger.info(f"\n[{step}/{total}] {title}")
        try:
            func()
        except Exception as e:
            logger.warning(f"  {title} lỗi: {e}")

    logger.info("\n" + "=" * 60)
    logger.info("HOÀN TẤT!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
