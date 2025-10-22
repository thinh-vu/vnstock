"""
Module xử lý dữ liệu tài chính từ FMP API.
Following VCI patterns for consistency.
"""

import pandas as pd
from typing import Optional
from vnstock.core.utils.logger import get_logger
from vnai import optimize_execution
from .config import FMPConfig, make_fmp_request

logger = get_logger(__name__)


class Financial:
    """
    Class xử lý dữ liệu tài chính từ FMP.
    """

    def __init__(self, symbol: str, api_key: Optional[str] = None,
                 show_log: Optional[bool] = True):
        """
        Khởi tạo Financial instance.

        Tham số:
            symbol (str): Mã chứng khoán (ticker symbol)
            api_key (Optional[str]): FMP API key
            show_log (Optional[bool]): Hiển thị log
        """
        self.symbol = symbol.upper()
        self.config = FMPConfig(api_key=api_key, show_log=show_log)
        self.show_log = show_log

    @optimize_execution(processing_label="Đang truy xuất báo cáo thu nhập")
    def income_statement(self, period: str = 'annual',
                         limit: int = 5) -> Optional[pd.DataFrame]:
        """
        Lấy báo cáo kết quả kinh doanh (Income Statement).

        Tham số:
            period (str): Chu kỳ báo cáo ('annual', 'quarter')
                         Mặc định: 'annual'
            limit (int): Số lượng báo cáo. Mặc định: 5

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa báo cáo thu nhập
        """
        url = self.config.get_endpoint_url('income_statement', self.symbol)
        url = f"{url}&period={period}&limit={limit}"

        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()
            # Chuyển đổi date columns
            self._convert_date_columns(df)

        return df

    @optimize_execution(processing_label="Đang truy xuất bảng cân đối kế toán")
    def balance_sheet(self, period: str = 'annual',
                      limit: int = 5) -> Optional[pd.DataFrame]:
        """
        Lấy bảng cân đối kế toán (Balance Sheet).

        Tham số:
            period (str): Chu kỳ báo cáo ('annual', 'quarter')
                         Mặc định: 'annual'
            limit (int): Số lượng báo cáo. Mặc định: 5

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa bảng cân đối kế toán
        """
        url = self.config.get_endpoint_url('balance_sheet', self.symbol)
        url = f"{url}&period={period}&limit={limit}"

        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()
            # Chuyển đổi date columns
            self._convert_date_columns(df)

        return df

    @optimize_execution(processing_label="Đang truy xuất báo cáo lưu chuyển tiền")
    def cashflow_statement(self, period: str = 'annual',
                           limit: int = 5) -> Optional[pd.DataFrame]:
        """
        Lấy báo cáo lưu chuyển tiền tệ (Cash Flow Statement).

        Tham số:
            period (str): Chu kỳ báo cáo ('annual', 'quarter')
                         Mặc định: 'annual'
            limit (int): Số lượng báo cáo. Mặc định: 5

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa báo cáo lưu chuyển tiền
        """
        url = self.config.get_endpoint_url(
            'cashflow_statement', self.symbol)
        url = f"{url}&period={period}&limit={limit}"

        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()
            # Chuyển đổi date columns
            self._convert_date_columns(df)

        return df

    @optimize_execution(processing_label="Đang truy xuất chỉ số tài chính")
    def ratios(self, period: str = 'annual',
               limit: int = 5) -> Optional[pd.DataFrame]:
        """
        Lấy các chỉ số tài chính (Financial Ratios).

        Tham số:
            period (str): Chu kỳ báo cáo ('annual', 'quarter')
                         Mặc định: 'annual'
            limit (int): Số lượng báo cáo. Mặc định: 5

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa chỉ số tài chính
        """
        url = self.config.get_endpoint_url('ratios', self.symbol)
        url = f"{url}&period={period}&limit={limit}"

        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()

        return df

    @optimize_execution(processing_label="Đang truy xuất chỉ số tăng trưởng")
    def growth(self, period: str = 'annual',
               limit: int = 5) -> Optional[pd.DataFrame]:
        """
        Lấy các chỉ số tăng trưởng (Financial Growth).

        Tham số:
            period (str): Chu kỳ báo cáo ('annual', 'quarter')
                         Mặc định: 'annual'
            limit (int): Số lượng báo cáo. Mặc định: 5

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa chỉ số tăng trưởng
        """
        url = self.config.get_endpoint_url('financial_growth', self.symbol)
        url = f"{url}&period={period}&limit={limit}"

        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()
            # Chuyển đổi date columns
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])

        return df

    @optimize_execution(processing_label="Đang truy xuất các chỉ số chính")
    def key_metrics(self, period: str = 'annual',
                    limit: int = 5) -> Optional[pd.DataFrame]:
        """
        Lấy các chỉ số chính (Key Metrics).

        Tham số:
            period (str): Chu kỳ báo cáo ('annual', 'quarter')
                         Mặc định: 'annual'
            limit (int): Số lượng báo cáo. Mặc định: 5

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa các chỉ số chính
        """
        url = self.config.get_endpoint_url('key_metrics', self.symbol)
        url = f"{url}&period={period}&limit={limit}"

        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()
            # Chuyển đổi date columns
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])

        return df

    @optimize_execution(processing_label="Đang truy xuất điểm sức khỏe tài chính")
    def financial_score(self) -> Optional[pd.DataFrame]:
        """
        Lấy điểm đánh giá sức khỏe tài chính.

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa điểm tài chính
        """
        url = self.config.get_endpoint_url('financial_score', self.symbol)
        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.upper()

        return df

    @optimize_execution(processing_label="Đang truy xuất thông tin cổ tức")
    def dividends(self) -> Optional[pd.DataFrame]:
        """
        Lấy lịch sử cổ tức.

        Returns:
            Optional[pd.DataFrame]: DataFrame chứa thông tin cổ tức
        """
        url = self.config.get_endpoint_url(
            'historical_dividends', self.symbol)
        df = make_fmp_request(url, timeout=self.config.timeout,
                              show_log=self.show_log)

        if df is not None and not df.empty:
            # Chuyển đổi date columns
            for date_col in ['date', 'paymentDate', 'recordDate',
                             'declarationDate']:
                if date_col in df.columns:
                    df[date_col] = pd.to_datetime(df[date_col])

        return df

    def _convert_date_columns(self, df: pd.DataFrame) -> None:
        """
        Chuyển đổi các cột ngày tháng sang datetime.

        Tham số:
            df (pd.DataFrame): DataFrame cần chuyển đổi
        """
        date_columns = ['date', 'fillingDate', 'acceptedDate',
                       'calendarYear', 'period']

        for col in date_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    # Nếu không chuyển đổi được, giữ nguyên
                    pass
