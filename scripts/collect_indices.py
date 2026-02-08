"""
Thu thập dữ liệu lịch sử các chỉ số chứng khoán Việt Nam + biểu đồ trực quan.

Chỉ số: VNINDEX, HNXINDEX, UPCOMINDEX, VN30, HNX30

Output:
    data/indices/
    ├── VNINDEX.csv
    ├── HNXINDEX.csv
    ├── UPCOMINDEX.csv
    ├── VN30.csv
    ├── HNX30.csv
    ├── all_indices.csv          # Gộp tất cả
    └── charts/
        ├── overview.png         # Tổng quan tất cả chỉ số
        ├── VNINDEX.png          # Chart riêng từng chỉ số
        ├── HNXINDEX.png
        ├── UPCOMINDEX.png
        ├── VN30.png
        ├── HNX30.png
        └── volume_comparison.png

Cách chạy:
    python scripts/collect_indices.py                                    # 1 năm gần nhất
    python scripts/collect_indices.py --start 2024-01-01                 # Từ ngày cụ thể
    python scripts/collect_indices.py --start 2020-01-01 --end 2026-02-08  # Khoảng thời gian
"""

import sys
import time
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

# ============================================================
# CẤU HÌNH
# ============================================================

INDICES = ["VNINDEX", "HNXINDEX", "UPCOMINDEX", "VN30", "HNX30"]

INDEX_LABELS = {
    "VNINDEX": "VN-Index",
    "HNXINDEX": "HNX-Index",
    "UPCOMINDEX": "UPCOM-Index",
    "VN30": "VN30",
    "HNX30": "HNX30",
}

INDEX_COLORS = {
    "VNINDEX": "#E53935",
    "HNXINDEX": "#1E88E5",
    "UPCOMINDEX": "#43A047",
    "VN30": "#FB8C00",
    "HNX30": "#8E24AA",
}

DATA_DIR = PROJECT_ROOT / "data" / "indices"
CHART_DIR = DATA_DIR / "charts"

# Dùng KBS vì hỗ trợ đủ 5 chỉ số (VCI thiếu VN30, HNX30)
SOURCE = "KBS"

REQUEST_DELAY = 0.5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("indices")


# ============================================================
# THU THẬP DỮ LIỆU
# ============================================================

def fetch_index_history(symbol: str, start: str, end: str) -> pd.DataFrame:
    """Lấy dữ liệu OHLCV lịch sử cho 1 chỉ số."""
    from vnstock.common.client import Vnstock

    logger.info(f"  Đang lấy {symbol} ({start} -> {end})...")
    client = Vnstock(source=SOURCE, show_log=False)
    stock = client.stock(symbol=symbol, source=SOURCE)
    df = stock.quote.history(start=start, end=end, interval="1D")
    if df is not None and not df.empty:
        df["symbol"] = symbol
        logger.info(f"  {symbol}: {len(df)} phiên giao dịch")
    else:
        logger.warning(f"  {symbol}: Không có dữ liệu")
    return df


def collect_all_indices(start: str, end: str) -> dict:
    """Lấy dữ liệu tất cả chỉ số. Trả về dict {symbol: DataFrame}."""
    results = {}
    for symbol in INDICES:
        try:
            df = fetch_index_history(symbol, start, end)
            if df is not None and not df.empty:
                results[symbol] = df
        except Exception as e:
            logger.error(f"  Lỗi {symbol}: {e}")
        time.sleep(REQUEST_DELAY)
    return results


# ============================================================
# TÍNH CHỈ SỐ KỸ THUẬT
# ============================================================

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Thêm các chỉ số kỹ thuật cơ bản vào DataFrame."""
    df = df.copy()
    close = df["close"]

    # Moving Averages
    for p in [20, 50, 200]:
        df[f"sma_{p}"] = close.rolling(window=p, min_periods=1).mean()

    # RSI 14
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14).mean()
    rs = avg_gain / avg_loss
    df["rsi_14"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    # Bollinger Bands
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    df["bb_upper"] = sma20 + 2 * std20
    df["bb_lower"] = sma20 - 2 * std20

    # Biến động
    df["daily_return"] = close.pct_change() * 100
    df["volatility_20d"] = df["daily_return"].rolling(20).std()

    return df


# ============================================================
# BIỂU ĐỒ TRỰC QUAN
# ============================================================

def setup_chart_style():
    """Thiết lập style chung cho biểu đồ."""
    plt.rcParams.update({
        "figure.facecolor": "#FAFAFA",
        "axes.facecolor": "#FFFFFF",
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linestyle": "--",
        "font.size": 10,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
    })


def chart_overview(data: dict, start: str, end: str):
    """Biểu đồ tổng quan: normalize tất cả chỉ số về cùng điểm xuất phát."""
    setup_chart_style()
    fig, axes = plt.subplots(2, 1, figsize=(16, 10), height_ratios=[3, 1],
                             gridspec_kw={"hspace": 0.3})

    # --- Panel 1: Giá chuẩn hóa (%) ---
    ax1 = axes[0]
    for symbol, df in data.items():
        if df.empty:
            continue
        base = df["close"].iloc[0]
        normalized = (df["close"] / base - 1) * 100
        ax1.plot(df["time"], normalized,
                 label=INDEX_LABELS[symbol],
                 color=INDEX_COLORS[symbol],
                 linewidth=1.5)

    ax1.set_title(f"So sanh cac chi so chung khoan Viet Nam ({start} - {end})")
    ax1.set_ylabel("Thay doi (%)")
    ax1.legend(loc="upper left", framealpha=0.9)
    ax1.axhline(y=0, color="black", linewidth=0.5, linestyle="-")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    fig.autofmt_xdate(rotation=45)

    # --- Panel 2: VNINDEX volume ---
    ax2 = axes[1]
    if "VNINDEX" in data and not data["VNINDEX"].empty:
        vn_df = data["VNINDEX"]
        colors = ["#E53935" if c < o else "#43A047"
                  for c, o in zip(vn_df["close"], vn_df["open"])]
        ax2.bar(vn_df["time"], vn_df["volume"], color=colors, alpha=0.6, width=1)
        ax2.set_ylabel("VNINDEX Volume")
        ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.0f}M"))
        ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
        ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))

    plt.savefig(CHART_DIR / "overview.png", dpi=150, bbox_inches="tight")
    plt.close()
    logger.info("  Saved: overview.png")


def chart_single_index(symbol: str, df: pd.DataFrame):
    """Biểu đồ chi tiết cho 1 chỉ số: Price + MA + Volume + RSI + MACD."""
    setup_chart_style()
    fig, axes = plt.subplots(4, 1, figsize=(16, 14),
                             height_ratios=[4, 1, 1.2, 1.2],
                             gridspec_kw={"hspace": 0.25})

    color = INDEX_COLORS[symbol]
    label = INDEX_LABELS[symbol]

    # --- Panel 1: Price + Bollinger + MA ---
    ax1 = axes[0]
    ax1.plot(df["time"], df["close"], color=color, linewidth=1.2, label="Close")
    ax1.plot(df["time"], df["sma_20"], color="#FF9800", linewidth=0.8, alpha=0.7, label="SMA 20")
    ax1.plot(df["time"], df["sma_50"], color="#2196F3", linewidth=0.8, alpha=0.7, label="SMA 50")
    ax1.plot(df["time"], df["sma_200"], color="#9C27B0", linewidth=0.8, alpha=0.7, label="SMA 200")
    ax1.fill_between(df["time"], df["bb_upper"], df["bb_lower"],
                     alpha=0.08, color=color, label="Bollinger Bands")
    ax1.set_title(f"{label} - Phan tich ky thuat")
    ax1.set_ylabel("Diem")
    ax1.legend(loc="upper left", fontsize=8, ncol=3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))

    # --- Panel 2: Volume ---
    ax2 = axes[1]
    colors = ["#E53935" if c < o else "#43A047"
              for c, o in zip(df["close"], df["open"])]
    ax2.bar(df["time"], df["volume"], color=colors, alpha=0.6, width=1)
    ax2.set_ylabel("Volume")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.0f}M"))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))

    # --- Panel 3: RSI ---
    ax3 = axes[2]
    ax3.plot(df["time"], df["rsi_14"], color=color, linewidth=1)
    ax3.axhline(y=70, color="#E53935", linewidth=0.8, linestyle="--", alpha=0.7)
    ax3.axhline(y=30, color="#43A047", linewidth=0.8, linestyle="--", alpha=0.7)
    ax3.fill_between(df["time"], 30, 70, alpha=0.05, color="gray")
    ax3.set_ylabel("RSI (14)")
    ax3.set_ylim(0, 100)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))

    # --- Panel 4: MACD ---
    ax4 = axes[3]
    ax4.plot(df["time"], df["macd"], color="#1E88E5", linewidth=1, label="MACD")
    ax4.plot(df["time"], df["macd_signal"], color="#E53935", linewidth=0.8, label="Signal")
    hist_colors = ["#43A047" if v >= 0 else "#E53935" for v in df["macd_hist"]]
    ax4.bar(df["time"], df["macd_hist"], color=hist_colors, alpha=0.5, width=1)
    ax4.axhline(y=0, color="black", linewidth=0.5)
    ax4.set_ylabel("MACD")
    ax4.legend(loc="upper left", fontsize=8)
    ax4.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))

    fig.autofmt_xdate(rotation=45)
    plt.savefig(CHART_DIR / f"{symbol}.png", dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"  Saved: {symbol}.png")


def chart_volume_comparison(data: dict):
    """So sánh khối lượng giao dịch giữa các sàn."""
    setup_chart_style()
    fig, axes = plt.subplots(len(data), 1, figsize=(16, 3 * len(data)),
                             gridspec_kw={"hspace": 0.4})

    if len(data) == 1:
        axes = [axes]

    for ax, (symbol, df) in zip(axes, data.items()):
        if df.empty:
            continue
        colors = ["#E53935" if c < o else "#43A047"
                  for c, o in zip(df["close"], df["open"])]
        ax.bar(df["time"], df["volume"], color=colors, alpha=0.6, width=1)
        ax.set_title(f"{INDEX_LABELS[symbol]} - Khoi luong giao dich", fontsize=11)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.0f}M"))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))

    fig.autofmt_xdate(rotation=45)
    plt.savefig(CHART_DIR / "volume_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()
    logger.info("  Saved: volume_comparison.png")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Thu thap du lieu lich su chi so chung khoan VN + bieu do.",
    )
    parser.add_argument("--start", default=None,
                        help="Ngay bat dau (YYYY-MM-DD). Mac dinh: 1 nam truoc")
    parser.add_argument("--end", default=None,
                        help="Ngay ket thuc (YYYY-MM-DD). Mac dinh: hom nay")
    args = parser.parse_args()

    end = args.end or datetime.now().strftime("%Y-%m-%d")
    start = args.start or (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info(f"THU THAP CHI SO CHUNG KHOAN VIET NAM")
    logger.info(f"Thoi gian: {start} -> {end}")
    logger.info(f"Chi so: {', '.join(INDICES)}")
    logger.info("=" * 60)

    # 1. Lấy dữ liệu
    logger.info("\n[1/3] LAY DU LIEU LICH SU")
    data = collect_all_indices(start, end)

    if not data:
        logger.error("Khong lay duoc du lieu nao. Dung lai.")
        return

    # 2. Lưu CSV + tính indicators
    logger.info("\n[2/3] LUU DU LIEU + TINH CHI SO KY THUAT")
    all_dfs = []
    for symbol, df in data.items():
        df = add_indicators(df)
        data[symbol] = df  # Cập nhật lại với indicators
        df.to_csv(DATA_DIR / f"{symbol}.csv", index=False, encoding="utf-8-sig")
        all_dfs.append(df)
        logger.info(f"  Saved: {symbol}.csv ({len(df)} dong)")

    # Gộp tất cả
    combined = pd.concat(all_dfs, ignore_index=True)
    combined.to_csv(DATA_DIR / "all_indices.csv", index=False, encoding="utf-8-sig")
    logger.info(f"  Saved: all_indices.csv ({len(combined)} dong)")

    # 3. Vẽ biểu đồ
    logger.info("\n[3/3] VE BIEU DO")
    chart_overview(data, start, end)
    for symbol, df in data.items():
        chart_single_index(symbol, df)
    chart_volume_comparison(data)

    logger.info("\n" + "=" * 60)
    logger.info(f"HOAN TAT!")
    logger.info(f"Du lieu: {DATA_DIR}")
    logger.info(f"Bieu do: {CHART_DIR}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
