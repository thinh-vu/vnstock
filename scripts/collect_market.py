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
# 1. FX RATES (MSN)
# ============================================================

def collect_fx(start: str, end: str):
    """Thu thập tỷ giá FX OHLCV từ MSN."""
    logger.info("Đang lấy tỷ giá FX từ MSN...")
    from vnstock.common.client import Vnstock

    fx_dir = DATA_DIR / "fx"
    fx_dir.mkdir(parents=True, exist_ok=True)

    success = 0
    errors = []

    for pair in FX_PAIRS:
        csv_path = fx_dir / f"{pair}.csv"

        # Determine fetch start for incremental update
        fetch_start = start
        existing_df = None
        if csv_path.exists():
            try:
                existing_df = pd.read_csv(csv_path, parse_dates=["time"])
                if not existing_df.empty:
                    last_date = existing_df["time"].max()
                    fetch_start = (last_date - timedelta(days=3)).strftime("%Y-%m-%d")
            except Exception:
                existing_df = None

        try:
            client = Vnstock(show_log=False)
            fx_obj = client.fx(symbol=pair, source="MSN")
            df = fx_obj.quote.history(start=fetch_start, end=end, interval="1D")

            if df is not None and not df.empty:
                df["symbol"] = pair

                if existing_df is not None and not existing_df.empty:
                    combined = pd.concat([existing_df, df])
                    combined = (
                        combined
                        .drop_duplicates("time", keep="last")
                        .sort_values("time")
                        .reset_index(drop=True)
                    )
                else:
                    combined = df.sort_values("time").reset_index(drop=True)

                combined.to_csv(csv_path, index=False, encoding="utf-8-sig")
                success += 1
                logger.info(f"  {pair}: {len(combined)} rows")
            else:
                errors.append(pair)
        except Exception as e:
            errors.append(pair)
            logger.warning(f"  {pair}: lỗi - {e}")

        time.sleep(0.5)

    logger.info(f"  FX: {success}/{len(FX_PAIRS)} OK, lỗi: {errors}")
    return success > 0


# ============================================================
# 2. CRYPTO (MSN)
# ============================================================

def collect_crypto(start: str, end: str):
    """Thu thập giá crypto OHLCV từ MSN."""
    logger.info("Đang lấy giá crypto từ MSN...")
    from vnstock.common.client import Vnstock

    crypto_dir = DATA_DIR / "crypto"
    crypto_dir.mkdir(parents=True, exist_ok=True)

    success = 0
    errors = []

    for symbol in CRYPTO_SYMBOLS:
        csv_path = crypto_dir / f"{symbol}.csv"

        fetch_start = start
        existing_df = None
        if csv_path.exists():
            try:
                existing_df = pd.read_csv(csv_path, parse_dates=["time"])
                if not existing_df.empty:
                    last_date = existing_df["time"].max()
                    fetch_start = (last_date - timedelta(days=3)).strftime("%Y-%m-%d")
            except Exception:
                existing_df = None

        try:
            client = Vnstock(show_log=False)
            crypto_obj = client.crypto(symbol=symbol, source="MSN")
            df = crypto_obj.quote.history(start=fetch_start, end=end, interval="1D")

            if df is not None and not df.empty:
                df["symbol"] = symbol

                if existing_df is not None and not existing_df.empty:
                    combined = pd.concat([existing_df, df])
                    combined = (
                        combined
                        .drop_duplicates("time", keep="last")
                        .sort_values("time")
                        .reset_index(drop=True)
                    )
                else:
                    combined = df.sort_values("time").reset_index(drop=True)

                combined.to_csv(csv_path, index=False, encoding="utf-8-sig")
                success += 1
                logger.info(f"  {symbol}: {len(combined)} rows")
            else:
                errors.append(symbol)
        except Exception as e:
            errors.append(symbol)
            logger.warning(f"  {symbol}: lỗi - {e}")

        time.sleep(0.5)

    logger.info(f"  Crypto: {success}/{len(CRYPTO_SYMBOLS)} OK, lỗi: {errors}")
    return success > 0


# ============================================================
# 3. WORLD INDICES (MSN)
# ============================================================

def collect_world_indices(start: str, end: str):
    """Thu thập chỉ số thế giới OHLCV từ MSN."""
    logger.info("Đang lấy chỉ số thế giới từ MSN...")
    from vnstock.common.client import Vnstock

    idx_dir = DATA_DIR / "world_indices"
    idx_dir.mkdir(parents=True, exist_ok=True)

    success = 0
    errors = []

    for symbol, name in WORLD_INDICES.items():
        csv_path = idx_dir / f"{symbol}.csv"

        fetch_start = start
        existing_df = None
        if csv_path.exists():
            try:
                existing_df = pd.read_csv(csv_path, parse_dates=["time"])
                if not existing_df.empty:
                    last_date = existing_df["time"].max()
                    fetch_start = (last_date - timedelta(days=3)).strftime("%Y-%m-%d")
            except Exception:
                existing_df = None

        try:
            client = Vnstock(show_log=False)
            idx_obj = client.world_index(symbol=symbol, source="MSN")
            df = idx_obj.quote.history(start=fetch_start, end=end, interval="1D")

            if df is not None and not df.empty:
                df["symbol"] = symbol
                df["name"] = name

                if existing_df is not None and not existing_df.empty:
                    combined = pd.concat([existing_df, df])
                    combined = (
                        combined
                        .drop_duplicates("time", keep="last")
                        .sort_values("time")
                        .reset_index(drop=True)
                    )
                else:
                    combined = df.sort_values("time").reset_index(drop=True)

                combined.to_csv(csv_path, index=False, encoding="utf-8-sig")
                success += 1
                logger.info(f"  {symbol} ({name}): {len(combined)} rows")
            else:
                errors.append(symbol)
        except Exception as e:
            errors.append(symbol)
            logger.warning(f"  {symbol}: lỗi - {e}")

        time.sleep(0.5)

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

        # 1. Industry classification
        try:
            logger.info("  Lấy phân ngành ICB...")
            industries = stock.listing.industries_icb()
            if industries is not None and not industries.empty:
                industries.to_csv(meta_dir / "industries_icb.csv", index=False, encoding="utf-8-sig")
                logger.info(f"  ICB: {len(industries)} ngành")
                success += 1
        except Exception as e:
            logger.warning(f"  ICB lỗi: {e}")

        # 2. Symbols by industry
        try:
            logger.info("  Lấy mã theo ngành...")
            by_industry = stock.listing.symbols_by_industries()
            if by_industry is not None and not by_industry.empty:
                by_industry.to_csv(meta_dir / "symbols_by_industry.csv", index=False, encoding="utf-8-sig")
                logger.info(f"  By industry: {len(by_industry)} mã")
                success += 1
        except Exception as e:
            logger.warning(f"  By industry lỗi: {e}")

        # 3. Future indices
        try:
            logger.info("  Lấy hợp đồng tương lai...")
            futures = stock.listing.all_future_indices()
            if futures is not None and not futures.empty:
                futures.to_csv(meta_dir / "futures.csv", index=False, encoding="utf-8-sig")
                logger.info(f"  Futures: {len(futures)} mã")
                success += 1
        except Exception as e:
            logger.warning(f"  Futures lỗi: {e}")

        # 4. Covered warrants
        try:
            logger.info("  Lấy chứng quyền...")
            warrants = stock.listing.all_covered_warrant()
            if warrants is not None and not warrants.empty:
                warrants.to_csv(meta_dir / "covered_warrants.csv", index=False, encoding="utf-8-sig")
                logger.info(f"  Warrants: {len(warrants)} mã")
                success += 1
        except Exception as e:
            logger.warning(f"  Warrants lỗi: {e}")

        # 5. Corporate bonds
        try:
            logger.info("  Lấy trái phiếu doanh nghiệp...")
            bonds = stock.listing.all_bonds()
            if bonds is not None and not bonds.empty:
                bonds.to_csv(meta_dir / "corporate_bonds.csv", index=False, encoding="utf-8-sig")
                logger.info(f"  Bonds: {len(bonds)} mã")
                success += 1
        except Exception as e:
            logger.warning(f"  Bonds lỗi: {e}")

        # 6. Government bonds
        try:
            logger.info("  Lấy trái phiếu chính phủ...")
            gov_bonds = stock.listing.all_government_bonds()
            if gov_bonds is not None and not gov_bonds.empty:
                gov_bonds.to_csv(meta_dir / "government_bonds.csv", index=False, encoding="utf-8-sig")
                logger.info(f"  Gov bonds: {len(gov_bonds)} mã")
                success += 1
        except Exception as e:
            logger.warning(f"  Gov bonds lỗi: {e}")

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

    sections = {
        "fx": ("FX RATES (MSN)", lambda: collect_fx(start, end)),
        "crypto": ("CRYPTO (MSN)", lambda: collect_crypto(start, end)),
        "world": ("WORLD INDICES (MSN)", lambda: collect_world_indices(start, end)),
        "fund": ("FUND DATA (FMARKET)", collect_fund_data),
        "listing": ("LISTING METADATA (KBS)", collect_listing_metadata),
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
