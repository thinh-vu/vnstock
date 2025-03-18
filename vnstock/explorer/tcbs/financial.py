"""
Module quản lý thông tin báo cáo tài chính từ nguồn dữ liệu TCBS.
"""

import pandas as pd
from typing import Optional, Dict, Union
from vnstock.core.utils import client
from vnstock.core.utils.parser import get_asset_type, camel_to_snake
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers
from vnai import optimize_execution  # Import the decorator from vnai package
from .const import _BASE_URL, _ANALYSIS_URL, _FINANCIAL_REPORT_MAP, _FINANCIAL_REPORT_PERIOD_MAP

logger = get_logger(__name__)


class Finance:
    """
    Truy xuất thông tin báo cáo tài chính của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

    Tham số:
        - symbol (str): Mã chứng khoán của công ty cần truy xuất thông tin.
        - report_type (str): Loại báo cáo tài chính cần truy xuất. Mặc định là 'income_statement'.
        - period (str): Chu kỳ báo cáo tài chính cần truy xuất. Mặc định là 'quarterly'.
        - get_all (bool): Truy xuất toàn bộ thông tin báo cáo tài chính hoặc không. Mặc định là True.
        - show_log (bool): Hiển thị thông tin log hoặc không. Mặc định là True.
    """

    def __init__(self, symbol: str, report_type: Optional[str] = 'income_statement', 
                 period: Optional[str] = 'quarter', get_all: Optional[bool] = True, 
                 show_log: Optional[bool] = True):
        """
        Khởi tạo đối tượng Finance với các tham số cho việc truy xuất dữ liệu báo cáo tài chính.
        """
        self.symbol = symbol.upper()
        self.asset_type = get_asset_type(self.symbol)
        self.headers = get_headers(data_source='TCBS')
        self.show_log = show_log
        
        # Validate input for report_type
        if report_type not in ['balance_sheet', 'income_statement', 'cash_flow']:
            raise ValueError("Loại báo cáo tài chính không hợp lệ. Chỉ chấp nhận 'balance_sheet', 'income_statement', 'cash_flow'.")
        
        # Validate input for period
        if period not in ['year', 'quarter']:
            raise ValueError("Kỳ báo cáo tài chính không hợp lệ. Chỉ chấp nhận 'year' hoặc 'quarter'.")
        
        # If asset_type is not stock, raise error
        if self.asset_type not in ['stock']:
            raise ValueError("Mã chứng khoán không hợp lệ. Chỉ cổ phiếu mới có thông tin.")
            
        self.report_type = _FINANCIAL_REPORT_MAP.get(report_type)
        self.period = _FINANCIAL_REPORT_PERIOD_MAP.get(period)
        self.get_all = get_all

        if not show_log:
            logger.setLevel('CRITICAL')
    
    def _get_report(self, report_type: Optional[str] = 'balance_sheet', 
                   period: Optional[str] = 'quarter', dropna: Optional[bool] = True, 
                   get_all: Optional[bool] = True, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Truy xuất thông tin báo cáo tài chính của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - report_type (str): Loại báo cáo tài chính cần truy xuất. Mặc định là 'balance_sheet'.
            - period (str): Chu kỳ báo cáo tài chính cần truy xuất. Mặc định là 'quarter'.
            - dropna (bool): Loại bỏ cột nào có giá trị NaN hoặc không. Mặc định là True.
            - get_all (bool): Truy xuất toàn bộ thông tin báo cáo tài chính hoặc không. Mặc định là True.
            - show_log (bool): Hiển thị thông tin log hoặc không. Mặc định là False.
            
        Returns:
            pd.DataFrame: DataFrame chứa dữ liệu báo cáo tài chính.
        """
        # Use instance attributes if parameters not provided
        effective_report_type = _FINANCIAL_REPORT_MAP.get(report_type, report_type) if report_type else self.report_type
        effective_period = _FINANCIAL_REPORT_PERIOD_MAP.get(period, period) if period else self.period
        effective_get_all = get_all if get_all is not None else self.get_all

        url = f'{_BASE_URL}/{_ANALYSIS_URL}/v1/finance/{self.symbol}/{effective_report_type}'
        params = {'yearly': effective_period, 'isAll': effective_get_all}
        
        try:
            # Use centralized API client instead of direct requests
            response_data = client.send_request(
                url=url,
                headers=self.headers,
                method="GET",
                params=params,
                show_log=show_log
            )
            
            df = pd.DataFrame(response_data)

            # Set year and quarter to string type
            df['year'] = df['year'].astype(str)
            df['quarter'] = df['quarter'].astype(str)

            if dropna:
                # Drop columns with all NaN values
                df.dropna(axis=1, how='all', inplace=True)

            if effective_report_type != 'cash_flow':
                if period == 'year':
                    df.drop(columns='quarter', inplace=True)
                    df.rename(columns={'year': 'period'}, inplace=True)
                elif period == 'quarter':
                    df['period'] = df['year'] + '-Q' + df['quarter']
                    # Rearrange columns to make period the first column
                    cols = df.columns.tolist()
                    cols = cols[-1:] + cols[:-1]
                    df = df[cols]

                df.set_index('period', inplace=True)

            df.name = self.symbol
            df.source = 'TCBS'
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving {report_type} report for {self.symbol}: {e}")
            if show_log:
                logger.exception("Detailed traceback:")
            return pd.DataFrame()  # Return empty DataFrame on error
    
    @optimize_execution("TCBS")
    def balance_sheet(self, period: Optional[str] = 'year', 
                     to_df: Optional[bool] = True, show_log: Optional[bool] = False) -> Union[pd.DataFrame, Dict]:
        """
        Truy xuất thông tin bảng cân đối kế toán (rút gọn) của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - period (str): Chu kỳ báo cáo tài chính cần truy xuất. Mặc định là 'year'.
            - to_df (bool): Chuyển đổi kết quả thành DataFrame hoặc không. Mặc định là True.
            - show_log (bool): Hiển thị thông tin log hoặc không. Mặc định là False.
            
        Returns:
            Union[pd.DataFrame, Dict]: DataFrame chứa dữ liệu bảng cân đối kế toán hoặc Dict dạng JSON.
        """
        # Validate input for period
        if period not in ['year', 'quarter']:
            raise ValueError("Kỳ báo cáo tài chính không hợp lệ. Chỉ chấp nhận 'year' hoặc 'quarter'.")
        
        df = self._get_report('balance_sheet', period=period, show_log=show_log)
        
        # Process only if DataFrame is not empty
        if not df.empty:
            df.drop(columns=['ticker'], inplace=True, errors='ignore')
            df.columns = [camel_to_snake(col) for col in df.columns]
            
        if to_df:
            return df
        else:
            return df.to_dict(orient='records')[0] if not df.empty else {}
    
    @optimize_execution("TCBS")
    def income_statement(self, period: Optional[str] = 'year', 
                        to_df: Optional[bool] = True, show_log: Optional[bool] = False) -> Union[pd.DataFrame, Dict]:
        """
        Truy xuất thông tin báo cáo kết quả kinh doanh của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - period (str): Chu kỳ báo cáo tài chính cần truy xuất. Mặc định là 'year'.
            - to_df (bool): Chuyển đổi kết quả thành DataFrame hoặc không. Mặc định là True.
            - show_log (bool): Hiển thị thông tin log hoặc không. Mặc định là False.
            
        Returns:
            Union[pd.DataFrame, Dict]: DataFrame chứa dữ liệu báo cáo kết quả kinh doanh hoặc Dict dạng JSON.
        """
        df = self._get_report('income_statement', period=period, show_log=show_log)
        
        # Process only if DataFrame is not empty
        if not df.empty:
            df.drop(columns=['ticker'], inplace=True, errors='ignore')
            df.columns = [camel_to_snake(col) for col in df.columns]
            
        if to_df:
            return df
        else:
            return df.to_dict(orient='records')[0] if not df.empty else {}
    
    @optimize_execution("TCBS")
    def cash_flow(self, period: Optional[str] = 'year', 
                 to_df: Optional[bool] = True, show_log: Optional[bool] = False) -> Union[pd.DataFrame, Dict]:
        """
        Truy xuất thông tin báo cáo lưu chuyển tiền tệ của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - period (str): Chu kỳ báo cáo tài chính cần truy xuất. Mặc định là 'year'.
            - to_df (bool): Chuyển đổi kết quả thành DataFrame hoặc không. Mặc định là True.
            - show_log (bool): Hiển thị thông tin log hoặc không. Mặc định là False.
            
        Returns:
            Union[pd.DataFrame, Dict]: DataFrame chứa dữ liệu báo cáo lưu chuyển tiền tệ hoặc Dict dạng JSON.
        """
        df = self._get_report('cash_flow', period=period, show_log=show_log)
        
        # Process only if DataFrame is not empty
        if not df.empty:
            df.drop(columns=['ticker'], inplace=True, errors='ignore')
            df.columns = [camel_to_snake(col) for col in df.columns]
            
        if to_df:
            return df
        else:
            return df.to_dict(orient='records')[0] if not df.empty else {}
    
    @optimize_execution("TCBS")
    def ratio(self, period: Optional[str] = 'quarter', dropna: Optional[bool] = True, 
             get_all: Optional[bool] = True, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Truy xuất thông tin chỉ số tài chính của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - period (str): Chu kỳ báo cáo tài chính cần truy xuất. Mặc định là 'quarter'.
            - dropna (bool): Loại bỏ cột nào có giá trị NaN hoặc không. Mặc định là True.
            - get_all (bool): Truy xuất toàn bộ thông tin chỉ số tài chính hoặc không. Mặc định là True.
            - show_log (bool): Hiển thị thông tin log hoặc không. Mặc định là False.
            
        Returns:
            pd.DataFrame: DataFrame chứa dữ liệu chỉ số tài chính.
        """
        effective_period = _FINANCIAL_REPORT_PERIOD_MAP.get(period, period) if period else self.period
        effective_get_all = get_all if get_all is not None else self.get_all

        url = f'{_BASE_URL}/{_ANALYSIS_URL}/v1/finance/{self.symbol}/financialratio'
        params = {'yearly': effective_period, 'isAll': str(effective_get_all).lower()}
        
        try:
            # Use centralized API client instead of direct requests
            response_data = client.send_request(
                url=url,
                headers=self.headers,
                method="GET",
                params=params,
                show_log=show_log
            )
            
            df = pd.DataFrame(response_data)
            
            # Process only if DataFrame is not empty
            if not df.empty:
                df.drop(columns='ticker', inplace=True, errors='ignore')
                df['year'] = df['year'].astype(str)

                if dropna:
                    # Drop columns with all NaN values
                    df.dropna(axis=1, how='all', inplace=True)

                if period == 'year':
                    df.drop(columns='quarter', inplace=True)
                    df.rename(columns={'year': 'period'}, inplace=True)
                elif period == 'quarter':
                    df['period'] = df['year'].astype(str) + '-Q' + df['quarter'].astype(str)
                    # Rearrange columns to make period the first column
                    cols = df.columns.tolist()
                    cols = cols[-1:] + cols[:-1]
                    df = df[cols]

                df.set_index('period', inplace=True)
                df.columns = [camel_to_snake(col) for col in df.columns]
                
            df.name = self.symbol
            df.source = 'TCBS'
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving financial ratios for {self.symbol}: {e}")
            if show_log:
                logger.exception("Detailed traceback:")
            return pd.DataFrame()  # Return empty DataFrame on error
