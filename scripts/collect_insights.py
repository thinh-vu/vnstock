"""
Thu thập thống kê thị trường / Market Insights từ vnstock_data Trading (source='cafef').

Yêu cầu: pip install vnstock_data (Insiders Program)

Output:
    data/insights/market_pe.csv          - P/E thị trường
    data/insights/market_pb.csv          - P/B thị trường
    data/insights/market_value.csv       - Giá trị giao dịch
    data/insights/market_volume.csv      - Khối lượng giao dịch
    data/insights/market_deal.csv        - Số lượng deal
    data/insights/foreign_buy.csv        - NDTNN mua
    data/insights/foreign_sell.csv       - NDTNN bán
    data/insights/top_gainer.csv         - Top tăng giá
    data/insights/top_loser.csv          - Top giảm giá
    data/insights/market_evaluation.csv  - Đánh giá thị trường

Cách chạy:
    python scripts/collect_insights.py                        # Tất cả
    python scripts/collect_insights.py --only pe pb foreign_buy  # Chỉ lấy 1 số loại
"""

import sys
import logging
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

# ============================================================
# CẤU HÌNH
# ============================================================

DATA_DIR = PROJECT_ROOT / "data" / "insights"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("insights")

# Market insights methods
INSIGHT_METHODS = [
    "pe",
    "pb",
    "value",
    "volume",
    "deal",
    "foreign_buy",
    "foreign_sell",
    "gainer",
    "loser",
    "evaluation",
]


# ============================================================
# COLLECTOR
# ============================================================

def collect_insights(only: list = None):
    """Thu thập thống kê thị trường từ vnstock_data Trading (source='cafef')."""
    try:
        from vnstock_data import Trading
    except ImportError:
        logger.error(
            "vnstock_data chưa được cài đặt. "
            "Package này thuộc Insiders Program. "
            "Liên hệ support@vnstocks.com để cài đặt."
        )
        return False

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Khởi tạo Trading(source='cafef', symbol='VNINDEX')")
    try:
        trading = Trading(source='cafef', symbol='VNINDEX')
    except Exception as e:
        logger.error(f"Không thể khởi tạo Trading(source='cafef'): {e}")
        return False

    methods = only if only else INSIGHT_METHODS
    success = 0
    errors = []

    for method_name in methods:
        csv_path = DATA_DIR / f"market_{method_name}.csv"

        try:
            method = getattr(trading, method_name, None)
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
                            # Snapshot - overwrite
                            pass
                    except Exception:
                        pass

                df.to_csv(csv_path, index=False, encoding="utf-8-sig")
                logger.info(f"  {method_name}: {len(df)} rows → {csv_path.name}")
                success += 1
            else:
                logger.warning(f"  {method_name}: không có dữ liệu.")
                errors.append(method_name)

        except NotImplementedError:
            logger.warning(f"  {method_name}: chưa hỗ trợ cho source 'cafef'.")
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
        description="Thu thập thống kê thị trường từ vnstock_data Trading (CafeF).",
    )
    parser.add_argument("--only", nargs="+", default=None,
                        help="Chỉ lấy 1 số chỉ số cụ thể")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("THU THẬP THỐNG KÊ THỊ TRƯỜNG (MARKET INSIGHTS)")
    logger.info(f"Nguồn: vnstock_data Trading (CafeF)")
    logger.info(f"Chỉ số: {args.only or 'Tất cả ' + str(len(INSIGHT_METHODS)) + ' loại'}")
    logger.info(f"Output: {DATA_DIR}")
    logger.info("=" * 60)

    collect_insights(only=args.only)

    logger.info("\n" + "=" * 60)
    logger.info("HOÀN TẤT!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
