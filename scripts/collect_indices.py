"""
Thu thập dữ liệu lịch sử chỉ số chứng khoán Việt Nam + biểu đồ trực quan.

Chỉ số chính (KBS):  VNINDEX, HNXINDEX, UPCOMINDEX, VN30, HNX30, VN100
Chỉ số ngành/quy mô/đầu tư (VCI direct API): VNMID, VNSML, VNFIN, VNREAL,
    VNIT, VNHEAL, VNENE, VNCONS, VNMAT, VNCOND, VNDIAMOND, VNFINSELECT

Output:
    data/indices/
    ├── VNINDEX.csv ... (CSV từng chỉ số)
    ├── all_indices.csv
    └── charts/
        ├── overview_main.png       # So sánh chỉ số chính
        ├── overview_sectors.png    # So sánh chỉ số ngành
        ├── overview_all.png        # Tất cả
        ├── VNINDEX.png ...         # Chart chi tiết: Price+MA+RSI+MACD
        └── volume_comparison.png

Cách chạy:
    python scripts/collect_indices.py                                      # 1 năm gần nhất
    python scripts/collect_indices.py --start 2024-01-01                   # Từ ngày cụ thể
    python scripts/collect_indices.py --start 2020-01-01 --end 2026-02-08  # Khoảng thời gian
"""

import sys
import time
import logging
import argparse
import requests
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

# Chỉ số chính (KBS hỗ trợ)
MAIN_INDICES = ["VNINDEX", "HNXINDEX", "UPCOMINDEX", "VN30", "HNX30"]

# Chỉ số quy mô (VCI direct)
SIZE_INDICES = ["VN100", "VNMID", "VNSML"]

# Chỉ số ngành (VCI direct)
SECTOR_INDICES = ["VNFIN", "VNREAL", "VNIT", "VNHEAL", "VNENE", "VNCONS", "VNMAT", "VNCOND"]

# Chỉ số đầu tư (VCI direct)
INVEST_INDICES = ["VNDIAMOND", "VNFINSELECT"]

# Toàn bộ 18 chỉ số
INDICES = MAIN_INDICES + SIZE_INDICES + SECTOR_INDICES + INVEST_INDICES

INDEX_LABELS = {
    # Chính
    "VNINDEX": "VN-Index",
    "HNXINDEX": "HNX-Index",
    "UPCOMINDEX": "UPCOM-Index",
    "VN30": "VN30",
    "HNX30": "HNX30",
    # Quy mô
    "VN100": "VN100",
    "VNMID": "VN-MidCap",
    "VNSML": "VN-SmallCap",
    # Ngành
    "VNFIN": "Tai chinh",
    "VNREAL": "Bat dong san",
    "VNIT": "Cong nghe",
    "VNHEAL": "Y te",
    "VNENE": "Nang luong",
    "VNCONS": "Tieu dung",
    "VNMAT": "Vat lieu",
    "VNCOND": "Hang tieu dung",
    # Đầu tư
    "VNDIAMOND": "VN Diamond",
    "VNFINSELECT": "VN FinSelect",
}

INDEX_COLORS = {
    # Chính
    "VNINDEX": "#E53935",
    "HNXINDEX": "#1E88E5",
    "UPCOMINDEX": "#43A047",
    "VN30": "#FB8C00",
    "HNX30": "#8E24AA",
    # Quy mô
    "VN100": "#00ACC1",
    "VNMID": "#5E35B1",
    "VNSML": "#F4511E",
    # Ngành
    "VNFIN": "#C62828",
    "VNREAL": "#AD1457",
    "VNIT": "#1565C0",
    "VNHEAL": "#2E7D32",
    "VNENE": "#EF6C00",
    "VNCONS": "#6A1B9A",
    "VNMAT": "#4E342E",
    "VNCOND": "#00838F",
    # Đầu tư
    "VNDIAMOND": "#FFD600",
    "VNFINSELECT": "#00C853",
}

DATA_DIR = PROJECT_ROOT / "data" / "indices"
CHART_DIR = DATA_DIR / "charts"

# KBS hỗ trợ 5 chỉ số chính (VN100 qua KBS chỉ trả 1 dòng -> dùng VCI)
KBS_INDICES = {"VNINDEX", "HNXINDEX", "UPCOMINDEX", "VN30", "HNX30"}

# VCI API endpoint (gọi trực tiếp, bỏ qua validation của vnstock)
_VCI_CHART_URL = "https://trading.vietcap.com.vn/api/chart/OHLCChart/gap-chart"
_VCI_HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://trading.vietcap.com.vn/",
    "Referer": "https://trading.vietcap.com.vn/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

REQUEST_DELAY = 0.5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("indices")


# ============================================================
# THU THẬP DỮ LIỆU
# ============================================================

def _fetch_kbs(symbol: str, start: str, end: str) -> pd.DataFrame:
    """Lấy dữ liệu index qua vnstock KBS (chỉ hỗ trợ 6 chỉ số chính)."""
    from vnstock.common.client import Vnstock

    client = Vnstock(source="KBS", show_log=False)
    stock = client.stock(symbol=symbol, source="KBS")
    df = stock.quote.history(start=start, end=end, interval="1D")
    return df


def _parse_timestamps(times):
    """
    Tự động detect format timestamp từ VCI API.
    VCI có thể trả timestamps dạng: seconds, milliseconds, hoặc string.
    """
    if not times:
        return pd.Series(dtype="datetime64[ns]")

    sample = times[0]

    # Nếu là string -> parse trực tiếp
    if isinstance(sample, str):
        return pd.to_datetime(times, errors="coerce")

    # Nếu là số -> detect seconds vs milliseconds
    val = abs(int(sample))
    if val > 1e12:
        # Milliseconds (> year 2001 as ms)
        return pd.to_datetime(times, unit="ms", errors="coerce")
    else:
        # Seconds
        return pd.to_datetime(times, unit="s", errors="coerce")


def _fetch_vci_direct(symbol: str, start: str, end: str) -> pd.DataFrame:
    """
    Lấy dữ liệu OHLCV từ VCI API trực tiếp (bỏ qua validation của vnstock).
    Dùng cho các chỉ số ngành/quy mô/đầu tư mà vnstock chưa hỗ trợ chính thức.
    """
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1)
    end_stamp = int(end_dt.timestamp())

    # Tính số phiên giao dịch (business days)
    bdays = len(pd.bdate_range(start=start_dt, end=end_dt))
    count_back = bdays + 10  # Thêm buffer

    payload = {
        "timeFrame": "ONE_DAY",
        "symbols": [symbol],
        "to": end_stamp,
        "countBack": count_back,
    }

    logger.info(f"    VCI payload: to={end_stamp}, countBack={count_back}")

    resp = requests.post(_VCI_CHART_URL, json=payload, headers=_VCI_HEADERS, timeout=30)

    # Log response status và nội dung nếu lỗi
    logger.info(f"    VCI response: status={resp.status_code}, content-type={resp.headers.get('content-type', 'unknown')}")

    if resp.status_code != 200:
        body_preview = resp.text[:500] if resp.text else "(empty)"
        logger.error(f"    VCI HTTP {resp.status_code}: {body_preview}")
        return pd.DataFrame()

    try:
        data = resp.json()
    except Exception as e:
        logger.error(f"    VCI JSON parse error: {e}. Body: {resp.text[:300]}")
        return pd.DataFrame()

    # Log response structure
    if isinstance(data, list):
        logger.info(f"    VCI data: list len={len(data)}")
        if data:
            keys = list(data[0].keys()) if isinstance(data[0], dict) else str(type(data[0]))
            logger.info(f"    VCI data[0] keys: {keys}")
    elif isinstance(data, dict):
        logger.info(f"    VCI data: dict keys={list(data.keys())}")
        # Nếu response là dict (có thể là error object)
        if "error" in data or "message" in data:
            logger.error(f"    VCI API error: {data}")
        return pd.DataFrame()
    else:
        logger.warning(f"    VCI data: unexpected type={type(data)}")
        return pd.DataFrame()

    if not data:
        logger.warning(f"  {symbol}: VCI API trả về rỗng")
        return pd.DataFrame()

    item = data[0]

    # VCI trả về dạng vector: {t: [...], o: [...], h: [...], l: [...], c: [...], v: [...]}
    times = item.get("t", [])
    opens = item.get("o", [])
    highs = item.get("h", [])
    lows = item.get("l", [])
    closes = item.get("c", [])
    volumes = item.get("v", [])

    if not times:
        logger.warning(f"  {symbol}: Không có dữ liệu từ VCI (t=[])")
        return pd.DataFrame()

    # Log timestamp sample để debug
    sample_t = times[0] if times else None
    logger.info(f"    Timestamps: count={len(times)}, sample={sample_t}, type={type(sample_t).__name__}")

    # Parse timestamps tự động
    time_series = _parse_timestamps(times)

    df = pd.DataFrame({
        "time": time_series,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })

    # Bỏ hàng có time NaT
    df = df.dropna(subset=["time"])

    # Lọc theo khoảng thời gian
    df = df[(df["time"] >= start) & (df["time"] <= end)]
    df = df.sort_values("time").reset_index(drop=True)

    # Đảm bảo dtype
    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0).astype("int64")

    return df


def fetch_index_history(symbol: str, start: str, end: str) -> pd.DataFrame:
    """
    Lấy dữ liệu OHLCV lịch sử cho 1 chỉ số.
    - KBS cho 6 chỉ số chính (VNINDEX, HNXINDEX, UPCOMINDEX, VN30, HNX30, VN100)
    - VCI direct API cho chỉ số ngành/quy mô/đầu tư
    """
    if symbol in KBS_INDICES:
        source = "KBS"
        logger.info(f"  Dang lay {symbol} [{source}] ({start} -> {end})...")
        df = _fetch_kbs(symbol, start, end)
    else:
        source = "VCI-direct"
        logger.info(f"  Dang lay {symbol} [{source}] ({start} -> {end})...")
        df = _fetch_vci_direct(symbol, start, end)

    if df is not None and not df.empty:
        df["symbol"] = symbol
        logger.info(f"  {symbol}: {len(df)} phien giao dich")
    else:
        logger.warning(f"  {symbol}: Khong co du lieu")
    return df


def collect_all_indices(start: str, end: str) -> dict:
    """Lấy dữ liệu tất cả chỉ số. Trả về dict {symbol: DataFrame}."""
    results = {}
    failed = []
    for symbol in INDICES:
        try:
            df = fetch_index_history(symbol, start, end)
            if df is not None and not df.empty and len(df) > 1:
                results[symbol] = df
            else:
                failed.append(symbol)
        except Exception as e:
            failed.append(symbol)
            logger.error(f"  Loi {symbol}: {e}")
        time.sleep(REQUEST_DELAY)

    if failed:
        logger.warning(f"  Khong lay duoc: {', '.join(failed)}")
    logger.info(f"  Thanh cong: {len(results)}/{len(INDICES)} chi so")
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


def _chart_group(data: dict, symbols: list, title: str, filename: str, start: str, end: str):
    """Vẽ biểu đồ so sánh cho 1 nhóm chỉ số (normalize %)."""
    setup_chart_style()
    group_data = {s: data[s] for s in symbols if s in data and not data[s].empty}
    if not group_data:
        return

    fig, ax = plt.subplots(figsize=(16, 7))

    for symbol, df in group_data.items():
        base = df["close"].iloc[0]
        normalized = (df["close"] / base - 1) * 100
        ax.plot(df["time"], normalized,
                label=INDEX_LABELS.get(symbol, symbol),
                color=INDEX_COLORS.get(symbol, "#333333"),
                linewidth=1.5)

    ax.set_title(f"{title} ({start} - {end})")
    ax.set_ylabel("Thay doi (%)")
    ax.legend(loc="upper left", framealpha=0.9, fontsize=9)
    ax.axhline(y=0, color="black", linewidth=0.5, linestyle="-")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    fig.autofmt_xdate(rotation=45)

    plt.savefig(CHART_DIR / filename, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"  Saved: {filename}")


def chart_overview(data: dict, start: str, end: str):
    """Vẽ nhiều biểu đồ tổng quan theo nhóm."""
    # 1. Chỉ số chính
    _chart_group(data, MAIN_INDICES,
                 "Chi so chinh", "overview_main.png", start, end)

    # 2. Chỉ số quy mô
    _chart_group(data, SIZE_INDICES,
                 "Chi so quy mo", "overview_size.png", start, end)

    # 3. Chỉ số ngành
    _chart_group(data, SECTOR_INDICES,
                 "Chi so nganh", "overview_sectors.png", start, end)

    # 4. Chỉ số đầu tư
    _chart_group(data, INVEST_INDICES,
                 "Chi so dau tu", "overview_invest.png", start, end)

    # 5. Tổng hợp tất cả
    _chart_group(data, INDICES,
                 "Toan bo chi so", "overview_all.png", start, end)


def chart_single_index(symbol: str, df: pd.DataFrame):
    """Biểu đồ chi tiết cho 1 chỉ số: Price + MA + Volume + RSI + MACD."""
    setup_chart_style()
    fig, axes = plt.subplots(4, 1, figsize=(16, 14),
                             height_ratios=[4, 1, 1.2, 1.2],
                             gridspec_kw={"hspace": 0.25})

    color = INDEX_COLORS.get(symbol, "#333333")
    label = INDEX_LABELS.get(symbol, symbol)

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
    """So sánh khối lượng giao dịch giữa các chỉ số chính."""
    setup_chart_style()
    # Chỉ vẽ volume cho chỉ số chính (5 cái), tránh quá nhiều subplot
    vol_symbols = [s for s in MAIN_INDICES if s in data and not data[s].empty]
    if not vol_symbols:
        return

    fig, axes = plt.subplots(len(vol_symbols), 1, figsize=(16, 3 * len(vol_symbols)),
                             gridspec_kw={"hspace": 0.4})

    if len(vol_symbols) == 1:
        axes = [axes]

    for ax, symbol in zip(axes, vol_symbols):
        df = data[symbol]
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
    logger.info(f"KBS (6 chinh): {', '.join(sorted(KBS_INDICES))}")
    logger.info(f"VCI direct (12 nganh/quy mo/dau tu): {', '.join(s for s in INDICES if s not in KBS_INDICES)}")
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
