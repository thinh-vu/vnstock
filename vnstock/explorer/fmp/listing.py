"""
Module xử lý danh sách và tìm kiếm chứng khoán từ FMP API.
Following VCI patterns for consistency.
"""

import pandas as pd
from typing import Optional
from vnstock.core.utils.logger import get_logger
from vnai import optimize_execution
from .config import FMPConfig, make_fmp_request

logger = get_logger(__name__)


class Listing:
    """
    Class xử lý danh sách và tìm kiếm chứng khoán từ FMP.
    """

    def __init__(self, api_key: Optional[str] = None,
                 show_log: Optional[bool] = True):
        """
        Khởi tạo Listing instance.

        Tham số:
            api_key (Optional[str]): FMP API key
            show_log (Optional[bool]): Hiển thị log
        """
        self.config = FMPConfig(api_key=api_key, show_log=show_log)
        self.show_log = show_log

    @optimize_execution(processing_label="Đang tìm kiếm mã chứng khoán")
    def search(self, query: str, limit: int = 10) -> Optional[pd.DataFrame]:
        """
        Tìm kiếm mã chứng khoán theo tên hoặc ticker.

        Tham số:
            query (str): Từ khóa tìm kiếm
            limit (int): Số lượng kết quả. Mặc định: 10

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa kết quả tìm kiếm
        """
        url = self.config.get_endpoint_url('search_symbol', query=query)
        url = f"{url}&limit={limit}"

        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()

        return df

    @optimize_execution(processing_label="Đang lấy danh sách cổ phiếu")
    def all_stocks(self) -> Optional[pd.DataFrame]:
        """
        Lấy danh sách tất cả cổ phiếu.

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa danh sách cổ phiếu
        """
        url = self.config.get_endpoint_url('stock_list')
        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()

        return df

    @optimize_execution(processing_label="Đang lấy danh sách ETF")
    def all_etfs(self) -> Optional[pd.DataFrame]:
        """
        Lấy danh sách tất cả ETF.

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa danh sách ETF
        """
        url = self.config.get_endpoint_url('etf_list')
        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()

        return df

    @optimize_execution(
        processing_label="Đang lấy danh sách chứng khoán giao dịch")
    def available_traded(self) -> Optional[pd.DataFrame]:
        """
        Lấy danh sách các chứng khoán đang được giao dịch.

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa danh sách
        """
        url = self.config.get_endpoint_url('available_traded')
        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()

        return df
