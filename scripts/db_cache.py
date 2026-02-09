"""
SQLite cache cho dữ liệu chỉ số và cổ phiếu.

Tránh gọi API lặp lại cho dữ liệu đã có.
- Lần đầu: fetch API → lưu vào SQLite
- Lần sau: đọc cache, chỉ fetch ngày chưa có

Database: data/cache.db
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "cache.db"

logger = logging.getLogger("db_cache")


def get_connection() -> sqlite3.Connection:
    """Tạo connection tới SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Tạo các bảng nếu chưa có."""
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS index_ohlcv (
            symbol TEXT NOT NULL,
            date   TEXT NOT NULL,
            open   REAL,
            high   REAL,
            low    REAL,
            close  REAL,
            volume INTEGER,
            PRIMARY KEY (symbol, date)
        );

        CREATE TABLE IF NOT EXISTS stock_ohlcv (
            symbol TEXT NOT NULL,
            date   TEXT NOT NULL,
            open   REAL,
            high   REAL,
            low    REAL,
            close  REAL,
            volume INTEGER,
            PRIMARY KEY (symbol, date)
        );

        CREATE TABLE IF NOT EXISTS price_board (
            symbol         TEXT NOT NULL,
            date           TEXT NOT NULL,
            close_price    REAL,
            percent_change REAL,
            total_trades   INTEGER,
            total_value    REAL,
            PRIMARY KEY (symbol, date)
        );
    """)
    conn.commit()
    conn.close()


# ============================================================
# INDEX OHLCV CACHE
# ============================================================

def get_cached_index(symbol: str, start: str, end: str) -> pd.DataFrame:
    """Đọc dữ liệu index OHLCV từ cache."""
    conn = get_connection()
    init_db()
    query = """
        SELECT date as time, open, high, low, close, volume
        FROM index_ohlcv
        WHERE symbol = ? AND date >= ? AND date <= ?
        ORDER BY date
    """
    df = pd.read_sql_query(query, conn, params=(symbol, start, end))
    conn.close()

    if not df.empty:
        df["time"] = pd.to_datetime(df["time"])

    return df


def save_index_data(symbol: str, df: pd.DataFrame):
    """Lưu dữ liệu index OHLCV vào cache (upsert)."""
    if df is None or df.empty:
        return

    conn = get_connection()
    init_db()

    rows = []
    for _, row in df.iterrows():
        date_str = row["time"]
        if hasattr(date_str, "strftime"):
            date_str = date_str.strftime("%Y-%m-%d")

        rows.append((
            symbol, date_str,
            float(row["open"]) if pd.notna(row["open"]) else None,
            float(row["high"]) if pd.notna(row["high"]) else None,
            float(row["low"]) if pd.notna(row["low"]) else None,
            float(row["close"]) if pd.notna(row["close"]) else None,
            int(row["volume"]) if pd.notna(row["volume"]) else 0,
        ))

    conn.executemany("""
        INSERT OR REPLACE INTO index_ohlcv (symbol, date, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    conn.close()
    logger.debug(f"  Cache: saved {len(rows)} rows for {symbol}")


def get_cached_dates(symbol: str, table: str = "index_ohlcv") -> set:
    """Lấy danh sách ngày đã có trong cache cho symbol."""
    conn = get_connection()
    init_db()
    cursor = conn.execute(
        f"SELECT date FROM {table} WHERE symbol = ?", (symbol,)
    )
    dates = {row[0] for row in cursor.fetchall()}
    conn.close()
    return dates


def get_last_cached_date(symbol: str, table: str = "index_ohlcv") -> str:
    """Lấy ngày cuối cùng trong cache cho symbol."""
    conn = get_connection()
    init_db()
    cursor = conn.execute(
        f"SELECT MAX(date) FROM {table} WHERE symbol = ?", (symbol,)
    )
    result = cursor.fetchone()[0]
    conn.close()
    return result


def get_cache_stats() -> dict:
    """Thống kê cache database."""
    conn = get_connection()
    init_db()
    stats = {}
    for table in ["index_ohlcv", "stock_ohlcv", "price_board"]:
        cursor = conn.execute(f"SELECT COUNT(*), COUNT(DISTINCT symbol) FROM {table}")
        rows, symbols = cursor.fetchone()
        stats[table] = {"rows": rows, "symbols": symbols}
    conn.close()
    return stats


# ============================================================
# STOCK OHLCV CACHE
# ============================================================

def get_cached_stock(symbol: str, start: str, end: str) -> pd.DataFrame:
    """Đọc dữ liệu stock OHLCV từ cache."""
    conn = get_connection()
    init_db()
    query = """
        SELECT date as time, open, high, low, close, volume
        FROM stock_ohlcv
        WHERE symbol = ? AND date >= ? AND date <= ?
        ORDER BY date
    """
    df = pd.read_sql_query(query, conn, params=(symbol, start, end))
    conn.close()

    if not df.empty:
        df["time"] = pd.to_datetime(df["time"])

    return df


def save_stock_data(symbol: str, df: pd.DataFrame):
    """Lưu dữ liệu stock OHLCV vào cache (upsert)."""
    if df is None or df.empty:
        return

    conn = get_connection()
    init_db()

    rows = []
    for _, row in df.iterrows():
        date_str = row.get("time", row.get("date", ""))
        if hasattr(date_str, "strftime"):
            date_str = date_str.strftime("%Y-%m-%d")

        rows.append((
            symbol, date_str,
            float(row["open"]) if pd.notna(row.get("open")) else None,
            float(row["high"]) if pd.notna(row.get("high")) else None,
            float(row["low"]) if pd.notna(row.get("low")) else None,
            float(row["close"]) if pd.notna(row.get("close")) else None,
            int(row["volume"]) if pd.notna(row.get("volume")) else 0,
        ))

    conn.executemany("""
        INSERT OR REPLACE INTO stock_ohlcv (symbol, date, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    conn.close()


# ============================================================
# UTILITIES
# ============================================================

def compute_fetch_range(symbol: str, start: str, end: str,
                        table: str = "index_ohlcv",
                        fresh_days: int = 3) -> tuple:
    """
    Tính khoảng ngày cần fetch từ API.

    Logic:
    - Nếu cache trống → fetch toàn bộ (start, end)
    - Nếu cache có dữ liệu → chỉ fetch từ (last_cached - fresh_days) đến end
      (fresh_days đầu được re-fetch để đảm bảo dữ liệu mới nhất chính xác)

    Returns:
        (fetch_start, fetch_end) hoặc (None, None) nếu cache đầy đủ
    """
    last = get_last_cached_date(symbol, table)
    if last is None:
        return start, end

    # Luôn re-fetch N ngày gần nhất để đảm bảo chính xác
    last_dt = datetime.strptime(last, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    refetch_from = (last_dt - timedelta(days=fresh_days)).strftime("%Y-%m-%d")

    if refetch_from > end:
        # Cache đã bao phủ toàn bộ range + fresh window
        return None, None

    return refetch_from, end
