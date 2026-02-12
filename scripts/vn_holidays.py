"""
Lịch nghỉ lễ sàn chứng khoán Việt Nam.

Nguồn: Thông báo của Ủy ban Chứng khoán Nhà nước (SSC) / Sở GDCK.
Cập nhật hàng năm khi có thông báo chính thức.

Sử dụng:
    python scripts/vn_holidays.py                  # Kiểm tra hôm nay
    python scripts/vn_holidays.py 2026-02-17       # Kiểm tra ngày cụ thể
    python scripts/vn_holidays.py --list 2026      # Liệt kê lịch nghỉ năm 2026
"""

import sys
from datetime import date

# ============================================================
# LỊCH NGHỈ LỄ SÀN CHỨNG KHOÁN VIỆT NAM
# Cập nhật theo thông báo UBCKNN mỗi năm
# ============================================================

HOLIDAYS = {
    # ==================== 2025 ====================
    2025: [
        # Tết Dương lịch
        "2025-01-01",
        # Tết Nguyên Đán Ất Tỵ (29 Tết - mùng 5)
        "2025-01-27",  # 28 Tết (nghỉ bù)
        "2025-01-28",  # 29 Tết
        "2025-01-29",  # 30 Tết
        "2025-01-30",  # Mùng 1
        "2025-01-31",  # Mùng 2
        "2025-02-03",  # Mùng 5 (nghỉ bù)
        # Giỗ Tổ Hùng Vương (10/3 Âm lịch)
        "2025-04-07",
        # Ngày Giải phóng miền Nam 30/4
        "2025-04-30",
        # Ngày Quốc tế Lao động 1/5
        "2025-05-01",
        # Ngày Quốc khánh 2/9
        "2025-09-01",  # Nghỉ bù
        "2025-09-02",
    ],

    # ==================== 2026 ====================
    # LƯU Ý: Cập nhật khi UBCKNN thông báo chính thức
    2026: [
        # Tết Dương lịch
        "2026-01-01",
        # Tết Nguyên Đán Bính Ngọ (ước tính, cần cập nhật)
        # Mùng 1 Tết = 17/02/2026
        "2026-02-16",  # 30 Tết
        "2026-02-17",  # Mùng 1
        "2026-02-18",  # Mùng 2
        "2026-02-19",  # Mùng 3
        "2026-02-20",  # Mùng 4
        # Giỗ Tổ Hùng Vương (10/3 Âm lịch ≈ 26/04/2026)
        "2026-04-24",  # Nghỉ bù (nếu rơi vào CN)
        # Ngày Giải phóng miền Nam 30/4
        "2026-04-30",
        # Ngày Quốc tế Lao động 1/5
        "2026-05-01",
        # Ngày Quốc khánh 2/9
        "2026-09-02",
    ],
}


def get_holidays(year: int = None) -> set:
    """Lấy danh sách ngày nghỉ lễ cho năm chỉ định."""
    if year is None:
        year = date.today().year
    return set(HOLIDAYS.get(year, []))


def is_holiday(check_date: str = None) -> bool:
    """
    Kiểm tra ngày có phải ngày nghỉ lễ không.

    Args:
        check_date: Ngày cần kiểm tra (YYYY-MM-DD). Mặc định: hôm nay.

    Returns:
        True nếu là ngày nghỉ lễ.
    """
    if check_date is None:
        check_date = date.today().strftime("%Y-%m-%d")

    year = int(check_date[:4])
    holidays = get_holidays(year)
    return check_date in holidays


def main():
    """CLI: kiểm tra ngày nghỉ lễ."""
    import argparse

    parser = argparse.ArgumentParser(description="Kiểm tra lịch nghỉ lễ TTCK Việt Nam")
    parser.add_argument("date", nargs="?", default=None,
                        help="Ngày kiểm tra (YYYY-MM-DD). Mặc định: hôm nay")
    parser.add_argument("--list", type=int, default=None, metavar="YEAR",
                        help="Liệt kê lịch nghỉ năm chỉ định")
    args = parser.parse_args()

    if args.list:
        holidays = sorted(get_holidays(args.list))
        if holidays:
            print(f"Lịch nghỉ lễ TTCK Việt Nam {args.list} ({len(holidays)} ngày):")
            for h in holidays:
                print(f"  {h}")
        else:
            print(f"Chưa có lịch nghỉ năm {args.list}. Cần cập nhật vn_holidays.py.")
        return

    check_date = args.date or date.today().strftime("%Y-%m-%d")

    if is_holiday(check_date):
        print(f"{check_date}: NGHỈ LỄ (sàn không giao dịch)")
        sys.exit(0)
    else:
        # Check weekend
        from datetime import datetime
        dt = datetime.strptime(check_date, "%Y-%m-%d")
        if dt.weekday() >= 5:
            print(f"{check_date}: CUỐI TUẦN (sàn không giao dịch)")
            sys.exit(0)
        else:
            print(f"{check_date}: NGÀY GIAO DỊCH")
            sys.exit(1)  # exit 1 = trading day (for shell: non-zero = should run)


if __name__ == "__main__":
    main()
