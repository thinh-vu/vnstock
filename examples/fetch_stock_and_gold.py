"""
Ví dụ: Lấy dữ liệu chứng khoán Việt Nam và giá vàng SJC.

Script này minh họa cách sử dụng thư viện vnstock để:
1. Lấy dữ liệu giá cổ phiếu lịch sử (OHLCV)
2. Lấy giá vàng SJC theo ngày
3. Lấy giá vàng BTMC (Bảo Tín Minh Châu)
4. Lấy thông tin công ty niêm yết
5. Lấy tỷ giá ngoại tệ VCB

Cách chạy:
    pip install vnstock
    python examples/fetch_stock_and_gold.py
"""

import sys
import os
from datetime import datetime, timedelta

# Thêm thư mục gốc vào path để import vnstock từ source
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd


# ============================================================
# 1. LẤY DỮ LIỆU CHỨNG KHOÁN VIỆT NAM
# ============================================================

def fetch_stock_history(symbol: str, start: str, end: str, source: str = "KBS"):
    """
    Lấy dữ liệu giá cổ phiếu lịch sử.

    Args:
        symbol: Mã cổ phiếu (VD: 'VNM', 'ACB', 'FPT', 'VCB')
        start: Ngày bắt đầu (YYYY-MM-DD)
        end: Ngày kết thúc (YYYY-MM-DD)
        source: Nguồn dữ liệu ('VCI', 'TCBS', 'KBS')

    Returns:
        DataFrame với các cột: time, open, high, low, close, volume
    """
    from vnstock.common.client import Vnstock

    stock_client = Vnstock(source=source, show_log=False)
    stock = stock_client.stock(symbol=symbol, source=source)
    df = stock.quote.history(start=start, end=end, interval='1D')
    return df


def fetch_stock_listing(source: str = "KBS"):
    """
    Lấy danh sách tất cả mã cổ phiếu niêm yết trên sàn.

    Args:
        source: Nguồn dữ liệu

    Returns:
        DataFrame chứa danh sách mã cổ phiếu
    """
    from vnstock.common.client import Vnstock

    stock_client = Vnstock(source=source, show_log=False)
    stock = stock_client.stock(symbol='ACB', source=source)
    df = stock.listing.all_symbols()
    return df


def fetch_company_overview(symbol: str, source: str = "TCBS"):
    """
    Lấy thông tin tổng quan về công ty.

    Args:
        symbol: Mã cổ phiếu
        source: Nguồn dữ liệu (TCBS hỗ trợ tốt nhất cho company info)

    Returns:
        DataFrame chứa thông tin công ty
    """
    from vnstock.common.client import Vnstock

    stock_client = Vnstock(source=source, show_log=False)
    stock = stock_client.stock(symbol=symbol, source=source)
    df = stock.company.overview()
    return df


def fetch_price_board(symbols: list, source: str = "KBS"):
    """
    Lấy bảng giá realtime của nhiều mã cổ phiếu.

    Args:
        symbols: Danh sách mã cổ phiếu (VD: ['VNM', 'ACB', 'FPT'])
        source: Nguồn dữ liệu

    Returns:
        DataFrame chứa bảng giá
    """
    from vnstock.common.client import Vnstock

    stock_client = Vnstock(source=source, show_log=False)
    stock = stock_client.stock(symbol=symbols[0], source=source)
    df = stock.trading.price_board(symbols_list=symbols)
    return df


# ============================================================
# 2. LẤY GIÁ VÀNG
# ============================================================

def fetch_sjc_gold_price(date: str = None):
    """
    Lấy giá vàng SJC theo ngày.

    Args:
        date: Ngày tra cứu (YYYY-MM-DD). Mặc định là ngày hôm nay.
              Dữ liệu có sẵn từ 2016-01-02.

    Returns:
        DataFrame với các cột: name, branch, buy_price, sell_price, date
    """
    from vnstock.explorer.misc.gold_price import sjc_gold_price

    df = sjc_gold_price(date=date)
    return df


def fetch_btmc_gold_price():
    """
    Lấy giá vàng Bảo Tín Minh Châu (BTMC) hiện tại.

    Returns:
        DataFrame với các cột: name, karat, gold_content, buy_price, sell_price, world_price, time
    """
    from vnstock.explorer.misc.gold_price import btmc_goldprice

    df = btmc_goldprice()
    return df


# ============================================================
# 3. LẤY TỶ GIÁ NGOẠI TỆ
# ============================================================

def fetch_exchange_rate(date: str = None):
    """
    Lấy tỷ giá ngoại tệ từ Vietcombank.

    Args:
        date: Ngày tra cứu (YYYY-MM-DD). Mặc định là hôm nay.

    Returns:
        DataFrame chứa tỷ giá
    """
    from vnstock.explorer.misc.exchange_rate import vcb_exchange_rate

    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    df = vcb_exchange_rate(date=date)
    return df


# ============================================================
# CHẠY DEMO
# ============================================================

def main():
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)
    pd.set_option('display.max_rows', 20)

    today = datetime.now().strftime('%Y-%m-%d')
    one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    # --- Giá vàng SJC ---
    print("=" * 70)
    print("GIÁ VÀNG SJC HÔM NAY")
    print("=" * 70)
    try:
        gold_df = fetch_sjc_gold_price()
        if gold_df is not None and not gold_df.empty:
            print(gold_df.to_string(index=False))
        else:
            print("Không có dữ liệu giá vàng SJC cho ngày hôm nay.")
    except Exception as e:
        print(f"Lỗi khi lấy giá vàng SJC: {e}")

    print()

    # --- Giá vàng BTMC ---
    print("=" * 70)
    print("GIÁ VÀNG BẢO TÍN MINH CHÂU (BTMC)")
    print("=" * 70)
    try:
        btmc_df = fetch_btmc_gold_price()
        if btmc_df is not None and not btmc_df.empty:
            print(btmc_df.to_string(index=False))
        else:
            print("Không có dữ liệu giá vàng BTMC.")
    except Exception as e:
        print(f"Lỗi khi lấy giá vàng BTMC: {e}")

    print()

    # --- Dữ liệu cổ phiếu ---
    symbols = ['VNM', 'ACB', 'FPT']
    print("=" * 70)
    print(f"DỮ LIỆU GIÁ CỔ PHIẾU ({one_month_ago} -> {today})")
    print("=" * 70)
    for symbol in symbols:
        print(f"\n--- {symbol} ---")
        try:
            stock_df = fetch_stock_history(symbol, start=one_month_ago, end=today)
            if stock_df is not None and not stock_df.empty:
                print(stock_df.tail(5).to_string(index=False))
            else:
                print(f"Không có dữ liệu cho {symbol}.")
        except Exception as e:
            print(f"Lỗi khi lấy dữ liệu {symbol}: {e}")

    print()

    # --- Tổng quan công ty ---
    print("=" * 70)
    print("THÔNG TIN CÔNG TY - VNM (Vinamilk)")
    print("=" * 70)
    try:
        company_df = fetch_company_overview('VNM')
        if company_df is not None:
            print(company_df.to_string())
        else:
            print("Không có dữ liệu công ty.")
    except Exception as e:
        print(f"Lỗi khi lấy thông tin công ty: {e}")

    print()

    # --- Tỷ giá ngoại tệ ---
    print("=" * 70)
    print("TỶ GIÁ NGOẠI TỆ VIETCOMBANK")
    print("=" * 70)
    try:
        fx_df = fetch_exchange_rate()
        if fx_df is not None and not fx_df.empty:
            print(fx_df.to_string(index=False))
        else:
            print("Không có dữ liệu tỷ giá.")
    except Exception as e:
        print(f"Lỗi khi lấy tỷ giá: {e}")


if __name__ == '__main__':
    main()
