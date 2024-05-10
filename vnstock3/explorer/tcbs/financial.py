# Thông tin tài chính, chỉ số tài chính
import pandas as pd
from pandas import json_normalize
import requests
from typing import Optional
from vnstock3.core.utils.parser import get_asset_type, camel_to_snake
from vnstock3.core.utils.logger import get_logger
from vnstock3.core.utils.user_agent import get_headers
from .const import _BASE_URL, _ANALYSIS_URL, _FINANCIAL_REPORT_MAP, _FINANCIAL_REPORT_PERIOD_MAP

logger = get_logger(__name__)

class Finance ():
    """
    Truy xuất thông tin báo cáo tài chính của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

    Tham số:
        - symbol (str): Mã chứng khoán của công ty cần truy xuất thông tin.
        - report_type (str): Loại báo cáo tài chính cần truy xuất. Mặc định là 'income_statement'.
        - period (str): Chu kỳ báo cáo tài chính cần truy xuất. Mặc định là 'quarterly'.
    """

    def __init__(self, symbol, report_type:Optional[str]='income_statement', period:Optional[str]='quarter', get_all:Optional[bool]=True):
        self.symbol = symbol.upper()
        self.asset_type = get_asset_type(self.symbol)
        self.headers = get_headers(data_source='TCBS')
        # validate input for report_type
        if report_type not in ['balance_sheet', 'income_statement', 'cash_flow']:
            raise ValueError("Loại báo cáo tài chính không hợp lệ. Chỉ chấp nhận 'balance_sheet', 'income_statement', 'cash_flow'.")
        # validate input for period
        if period not in ['year', 'quarter']:
            raise ValueError("Kỳ báo cáo tài chính không hợp lệ. Chỉ chấp nhận 'year' hoặc 'quarter'.")
        # if asset_type is not stock, raise error
        if self.asset_type not in ['stock']:
            raise ValueError("Mã chứng khoán không hợp lệ. Chỉ cổ phiếu mới có thông tin.")
        self.report_type = _FINANCIAL_REPORT_MAP.get(report_type)
        self.period = _FINANCIAL_REPORT_PERIOD_MAP.get(period)
        self.get_all = get_all

    def _get_report (self, report_type:Optional[str]='balance_sheet', period:Optional[str]='quarter', dropna:Optional[bool]=True, get_all:Optional[bool]=True, show_log:Optional[bool]=False):
        """
        Truy xuất thông tin báo cáo tài chính của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - report_type (str): Loại báo cáo tài chính cần truy xuất. Mặc định là 'income_statement'.
            - period (str): Chu kỳ báo cáo tài chính cần truy xuất. Mặc định là 'quarterly'.
            - get_all (bool): Truy xuất toàn bộ thông tin báo cáo tài chính hoặc không. Mặc định là True.
        """
        # Use instance attributes if parameters not provided
        effective_report_type = _FINANCIAL_REPORT_MAP.get(report_type, report_type) if report_type else self.report_type
        effective_period = _FINANCIAL_REPORT_PERIOD_MAP.get(period, period) if period else self.period
        effective_get_all = get_all if get_all is not None else self.get_all

        url = f'{_BASE_URL}/{_ANALYSIS_URL}/v1/finance/{self.symbol}/{effective_report_type}'
        params = {'yearly': effective_period, 'isAll': effective_get_all}
        if show_log:
            logger.info(f"Fetching financial report data for {self.symbol} from TCBS. URL: {url}. Params: {params}")
        response = requests.get(url, params=params, headers=self.headers)
        if response.status_code != 200:
            logger.error(f"Error fetching financial report data for {self.symbol}. Details: {response.text}")
        df = json_normalize(response.json())

        # set year and quarter to string type
        df['year'] = df['year'].astype(str)
        df['quarter'] = df['quarter'].astype(str)

        if dropna:
            # drop columns with all NaN values
            df.dropna(axis=1, how='all', inplace=True)

        if effective_report_type != 'cash_flow':
            if period == 'year':
                df.drop(columns='quarter', inplace=True)
                df.rename(columns={'year':'period'}, inplace=True)
            elif period == 'quarter':
                df['period'] = df['year'] + '-Q' + df['quarter']
                # rearrange columns to make period the first column
                cols = df.columns.tolist()
                cols = cols[-1:] + cols[:-1]
                df = df[cols]

        df.set_index('period', inplace=True)

        df.name = self.symbol
        df.source = 'TCBS'
        return df
    
    def balance_sheet (self, period:Optional[str]='year', to_df:Optional[bool]=True, show_log:Optional[bool]=False):
        """
        Truy xuất thông tin bản cân đối kế toán (rút gọn) của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - period (str): Chu kỳ báo cáo tài chính cần truy xuất. Mặc định là 'year'.
            - dropna (bool): Loại bỏ cột nào có giá trị NaN hoặc không. Mặc định là True.
        """
        # validate input for period
        if period not in ['year', 'quarter']:
            raise ValueError("Kỳ báo cáo tài chính không hợp lệ. Chỉ chấp nhận 'year' hoặc 'quarter'.")
        
        df = self._get_report('balance_sheet', period=period, show_log=show_log)
        df.drop(columns=['ticker'], inplace=True)
        df.columns = [camel_to_snake(col) for col in df.columns]
        if to_df:
            return df
        else:
            return df.to_dict(orient='records')[0]
    
    def income_statement (self, period:Optional[str]='year', to_df:Optional[bool]=True, show_log:Optional[bool]=False):
        """
        Truy xuất thông tin báo cáo doanh thu của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - period (str): Chu kỳ báo cáo tài chính cần truy xuất. Mặc định là 'year'.
            - dropna (bool): Loại bỏ cột nào có giá trị NaN hoặc không. Mặc định là True.
        """
        df = self._get_report('income_statement', period=period, show_log=show_log)
        df.drop(columns=['ticker'], inplace=True)
        df.columns = [camel_to_snake(col) for col in df.columns]
        if to_df:
            return df
        else:
            return df.to_dict(orient='records')[0]
    
    def cash_flow (self, period:Optional[str]='year', to_df:Optional[bool]=True, show_log:Optional[bool]=False):
        """
        Truy xuất thông tin báo cáo lưu chuyển tiền tệ của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - period (str): Chu kỳ báo cáo tài chính cần truy xuất. Mặc định là 'year'.
            - dropna (bool): Loại bỏ cột nào có giá trị NaN hoặc không. Mặc định là True.
        """
        df = self._get_report('cash_flow', period=period, show_log=show_log)
        df.drop(columns=['ticker'], inplace=True)
        df.columns = [camel_to_snake(col) for col in df.columns]
        if to_df:
            return df
        else:
            return df.to_dict(orient='records')[0]
    
    def ratio (self, period:Optional[str]='quarter', dropna:Optional[bool]=True, get_all:Optional[bool]=True, show_log:Optional[bool]=False):
        """
        Truy xuất thông tin chỉ số tài chính của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - period (str): Chu kỳ báo cáo tài chính cần truy xuất. Mặc định là 'quarter'.
            - dropna (bool): Loại bỏ cột nào có giá trị NaN hoặc không. Mặc định là True.
            - get_all (bool): Truy xuất toàn bộ thông tin chỉ số tài chính hoặc không. Mặc định là True.
        """
        effective_period = _FINANCIAL_REPORT_PERIOD_MAP.get(period, period) if period else self.period
        effective_get_all = get_all if get_all is not None else self.get_all

        url = f'https://apipubaws.tcbs.com.vn/tcanalysis/v1/finance/{self.symbol}/financialratio?yearly={effective_period}&isAll={str(effective_get_all).lower()}'
        if show_log:
            logger.info(f"Fetching financial ratio data for {self.symbol} from TCBS. URL: {url}")
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            logger.error(f"Error fetching financial ratio data for {self.symbol}. Details: {response.text}")
        df = json_normalize(response.json())
        df.drop(columns='ticker', inplace=True)
        df['year'] = df['year'].astype(str)

        if dropna:
            # drop columns with all NaN values
            df.dropna(axis=1, how='all', inplace=True)

        if period == 'year':
            df.drop(columns='quarter', inplace=True)
            df.rename(columns={'year':'period'}, inplace=True)
        elif period == 'quarter':
            df['period'] = df['year'] + '-Q' + df['quarter']
            # rearrange columns to make period the first column
            cols = df.columns.tolist()
            cols = cols[-1:] + cols[:-1]
            df = df[cols]

        df.set_index('period', inplace=True)

        df.columns = [camel_to_snake(col) for col in df.columns]
        df.name = self.symbol
        df.source = 'TCBS'
        return df