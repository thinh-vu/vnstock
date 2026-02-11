"""
Thu thập giá hàng hóa từ vnstock_data CommodityPrice (source='spl').

Yêu cầu: pip install vnstock_data (Insiders Program)

Output:
    data/commodity/gold_vn.csv        - Giá vàng Việt Nam (mua/bán)
    data/commodity/gold_global.csv    - Giá vàng thế giới OHLCV
    data/commodity/oil_crude.csv      - Giá dầu thô OHLCV
    data/commodity/gas_natural.csv    - Giá khí tự nhiên OHLCV
    data/commodity/gas_vn.csv         - Giá xăng Việt Nam (RON95/RON92/Dầu DO)
    data/commodity/coke.csv           - Giá than cốc OHLCV
    data/commodity/steel_d10.csv      - Giá thép cuộn D10
    data/commodity/iron_ore.csv       - Giá quặng sắt OHLCV
    data/commodity/steel_hrc.csv      - Giá thép cuộn cán nóng OHLCV
    data/commodity/fertilizer_ure.csv - Giá phân Ure OHLCV
    data/commodity/soybean.csv        - Giá đậu nành OHLCV
    data/commodity/corn.csv           - Giá ngô OHLCV
    data/commodity/sugar.csv          - Giá đường OHLCV
    data/commodity/pork_north_vn.csv  - Giá lợn hơi miền Bắc VN
    data/commodity/pork_china.csv     - Giá lợn hơi Trung Quốc

Cách chạy:
    python scripts/collect_commodity.py                          # Tất cả
    python scripts/collect_commodity.py --start 2024-01-01       # Từ ngày cụ thể
    python scripts/collect_commodity.py --only gold_vn oil_crude  # Chỉ lấy 1 số loại
"""

import sys
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import pandas as pd
from utils import init_rate_limiter

# ============================================================
# CẤU HÌNH
# ============================================================

DATA_DIR = PROJECT_ROOT / "data" / "commodity"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("commodity")

# Tất cả hàng hóa có sẵn
COMMODITY_METHODS = [
    "gold_vn",
    "gold_global",
    "oil_crude",
    "gas_natural",
    "gas_vn",
    "coke",
    "steel_d10",
    "iron_ore",
    "steel_hrc",
    "fertilizer_ure",
    "soybean",
    "corn",
    "sugar",
    "pork_north_vn",
    "pork_china",
]


# ============================================================
# COLLECTOR
# ============================================================

def collect_commodity(start: str, end: str, only: list = None):
    """Thu thập giá hàng hóa từ vnstock_data CommodityPrice."""
    try:
        from vnstock_data import CommodityPrice
    except ImportError:
        logger.error(
            "vnstock_data chưa được cài đặt. "
            "Package này thuộc Insiders Program. "
            "Liên hệ support@vnstocks.com để cài đặt."
        )
        return False

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    logger.info(f"Khởi tạo CommodityPrice(start='{start}', end='{end}', source='spl')")
    commodity = CommodityPrice(start=start, end=end, source='spl')

    methods = only if only else COMMODITY_METHODS
    success = 0
    errors = []

    for method_name in methods:
        csv_path = DATA_DIR / f"{method_name}.csv"

        try:
            method = getattr(commodity, method_name, None)
            if method is None:
                logger.warning(f"  {method_name}: method không tồn tại, bỏ qua.")
                errors.append(method_name)
                continue

            logger.info(f"  Đang lấy {method_name}...")
            df = method()

            if df is not None and not df.empty:
                # Incremental: merge with existing data
                if csv_path.exists():
                    try:
                        existing = pd.read_csv(csv_path)
                        # Find date column
                        date_col = None
                        for col in ['date', 'time', 'Date', 'Time']:
                            if col in df.columns:
                                date_col = col
                                break

                        if date_col:
                            df = pd.concat([existing, df], ignore_index=True)
                            df = df.drop_duplicates(subset=[date_col], keep="last")
                            df = df.sort_values(date_col).reset_index(drop=True)
                        else:
                            df = pd.concat([existing, df], ignore_index=True)
                            df = df.drop_duplicates(keep="last")
                    except Exception:
                        pass

                df.to_csv(csv_path, index=False, encoding="utf-8-sig")
                logger.info(f"  {method_name}: {len(df)} rows → {csv_path.name}")
                success += 1
            else:
                logger.warning(f"  {method_name}: không có dữ liệu.")
                errors.append(method_name)

        except NotImplementedError:
            logger.warning(f"  {method_name}: chưa hỗ trợ cho source 'spl'.")
            errors.append(method_name)
        except Exception as e:
            logger.warning(f"  {method_name}: lỗi - {e}")
            errors.append(method_name)

    logger.info(f"\nKết quả: {success}/{len(methods)} OK, lỗi: {errors}")
    return success > 0


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Thu thập giá hàng hóa từ vnstock_data CommodityPrice.",
    )
    parser.add_argument("--start", default=None,
                        help="Ngày bắt đầu (YYYY-MM-DD). Mặc định: 3 năm trước")
    parser.add_argument("--end", default=None,
                        help="Ngày kết thúc (YYYY-MM-DD). Mặc định: hôm nay")
    parser.add_argument("--only", nargs="+", default=None,
                        help="Chỉ lấy 1 số hàng hóa cụ thể")
    args = parser.parse_args()

    end = args.end or datetime.now().strftime("%Y-%m-%d")
    start = args.start or (datetime.now() - timedelta(days=365 * 3)).strftime("%Y-%m-%d")

    # Initialize rate limiter (registers API key for proper tier detection)
    init_rate_limiter()

    logger.info("=" * 60)
    logger.info("THU THẬP GIÁ HÀNG HÓA")
    logger.info(f"Thời gian: {start} -> {end}")
    logger.info(f"Nguồn: vnstock_data CommodityPrice (SPL)")
    logger.info(f"Hàng hóa: {args.only or 'Tất cả ' + str(len(COMMODITY_METHODS)) + ' loại'}")
    logger.info(f"Output: {DATA_DIR}")
    logger.info("=" * 60)

    collect_commodity(start, end, only=args.only)

    logger.info("\n" + "=" * 60)
    logger.info("HOÀN TẤT!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
