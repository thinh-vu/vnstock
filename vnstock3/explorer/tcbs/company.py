import pandas as pd
from pandas import json_normalize
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
from .const import _BASE_URL, _ANALYSIS_URL
from vnstock3.core.utils.parser import get_asset_type, camel_to_snake
from vnstock3.core.utils.logger import get_logger
from vnstock3.core.utils.user_agent import get_headers
from vnstock3.explorer.tcbs.financial import Finance

logger = get_logger(__name__)

class Company:
    """
    Class (lớp) quản lý các thông tin liên quan đến công ty từ nguồn dữ liệu TCBS.

    Tham số:
        - symbol (str): Mã chứng khoán của công ty cần truy xuất thông tin.
        - random_agent (bool): Sử dụng user-agent ngẫu nhiên hoặc không. Mặc định là False.
    """
    def __init__(self, symbol, random_agent=False, to_df:Optional[bool]=True, show_log:Optional[bool]=False):
        self.symbol = symbol.upper()
        self.asset_type = get_asset_type(self.symbol)
        # if asset_type is not stock, raise error
        if self.asset_type not in ['stock']:
            raise ValueError("Mã chứng khoán không hợp lệ. Chỉ cổ phiếu mới có thông tin.")
        self.base_url = _BASE_URL
        self.headers = get_headers(data_source='TCBS', random_agent=random_agent)
        self.show_log = show_log
        self.to_df = to_df
        self.finance = Finance(self.symbol)

    def overview (self) -> Dict:
        """
        Truy xuất thông tin tổng quan của mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - symbol: Mã chứng khoán cần truy xuất thông tin tổng quan.
        """
        url = f'{_BASE_URL}/{_ANALYSIS_URL}/v1/ticker/{self.symbol}/overview'
        if self.show_log:
            logger.info(f"Fetching company overview data for {self.symbol} from TCBS. URL: {url}")
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            logger.error(f"Error fetching company overview data for {self.symbol}. Details: {response.text}")
        data = response.json()
        df = pd.DataFrame(data, index=[0])
        df = df[['ticker', 'exchange', 'industry', 'companyType',
                'noShareholders', 'foreignPercent', 'outstandingShare', 'issueShare',
                'establishedYear', 'noEmployees',  
                'stockRating', 'deltaInWeek', 'deltaInMonth', 'deltaInYear', 
                'shortName', 'website', 'industryID', 'industryIDv2']]
        df.columns = [camel_to_snake(col) for col in df.columns]
        df.rename(columns={'industry_i_dv2':'industry_id_v2'}, inplace=True)
        
        try:
            df.drop(columns='ticker', inplace=True)
        except:
            pass

        df.name = self.symbol
        df.source = 'TCBS'

        if self.to_df:
            return df
        else:
            return df.to_dict(orient='records')[0]
    
    def profile (self) -> Dict:
        """
        Truy xuất thông tin mô tả công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.
        
        Tham số:
            - to_df (bool): Chuyển đổi dữ liệu thành DataFrame hoặc không. Mặc định là True.
            - show_log (bool): Hiển thị log hoặc không. Mặc định là False.
        """
        url = f"{_BASE_URL}/{_ANALYSIS_URL}/v1/company/{self.symbol}/overview"
        if self.show_log:
            logger.info(f"Fetching company profile data for {self.symbol} from TCBS. URL: {url}")
        response = requests.request("GET", url, headers=self.headers)
        if response.status_code != 200:
            logger.error(f"Error fetching company profile data for {self.symbol}. Details: {response.text}")
        df = json_normalize(response.json())
        for col in df.columns:
            try:
                df[col] = df[col].apply(lambda x: BeautifulSoup(x, 'html.parser').get_text())
                df[col] = df[col].str.replace('\n', ' ')
            except:
                pass
        df['ticker'] = self.symbol
        
        try:
            df.drop(columns=['id', 'ticker'], inplace=True)
        except:
            pass

        df.columns = [camel_to_snake(col) for col in df.columns]

        df.name = self.symbol
        df.source = 'TCBS'

        if self.to_df:
            return df
        else:
            return df.to_dict(orient='records')[0]
    
    def shareholders (self) -> Dict:
        """
        Truy xuất thông tin cổ đông lớn của công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - to_df (bool): Chuyển đổi dữ liệu thành DataFrame hoặc không. Mặc định là True.
            - show_log (bool): Hiển thị log hoặc không. Mặc định là False.
        """
        url = f"{_BASE_URL}/{_ANALYSIS_URL}/v1/company/{self.symbol}/large-share-holders"
        if self.show_log:
            logger.info(f"Fetching large shareholders data for {self.symbol} from TCBS. URL: {url}")
        response = requests.request("GET", url, headers=self.headers)
        if response.status_code != 200:
            logger.error(f"Error fetching large shareholders data for {self.symbol}. Details: {response.text}")
        df = json_normalize(response.json()['listShareHolder'])
        df.rename(columns={'name': 'shareHolder', 'ownPercent': 'shareOwnPercent'}, inplace=True)

        try:
            df.drop(columns=['no', 'ticker'], inplace=True)
        except:
            pass

        df.columns = [camel_to_snake(col) for col in df.columns]

        df.name = self.symbol
        df.source = 'TCBS'

        if self.to_df:
            return df
        else:
            return df.to_dict(orient='records')[0]
        
    def insider_deals (self, page_size:Optional[int]=20, page:Optional[int]=0) -> Dict:
        """
        Truy xuất thông tin giao dịch nội bộ của công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - page_size (int): Số lượng giao dịch trên mỗi trang. Mặc định là 20.
            - page (int): Trang cần truy xuất thông tin. Mặc định là 0.
            - to_df (bool): Chuyển đổi dữ liệu thành DataFrame hoặc không. Mặc định là True.
            - show_log (bool): Hiển thị log hoặc không. Mặc định là False.
        """
        url = f"{_BASE_URL}/{_ANALYSIS_URL}/v1/company/{self.symbol}/insider-dealing?page={page}&size={page_size}"
        response = requests.request("GET", url, headers=self.headers)
        if response.status_code != 200:
            logger.error(f"Error fetching insider deals data for {self.symbol}. Details: {response.text}")  
        df = json_normalize(response.json()['listInsiderDealing'])

        try:
            df.drop(columns=['no', 'ticker'], inplace=True)
        except:
            pass

        df.rename(columns={'anDate': 'dealAnnounceDate', 'dealingMethod': 'dealMethod', 'dealingAction': 'dealAction', 'quantity': 'dealQuantity', 'price': 'dealPrice', 'ratio': 'dealRatio'}, inplace=True)
        df['dealAnnounceDate'] = pd.to_datetime(df['dealAnnounceDate'], format='%d/%m/%y')
        df.sort_values(by='dealAnnounceDate', ascending=False, inplace=True)
        df['dealMethod'] = df['dealMethod'].copy().replace({1: 'Cổ đông lớn', 2: 'Cổ đông sáng lập', 0: 'Cổ đông nội bộ'}, inplace=True)
        df['dealAction'] = df['dealAction'].copy().replace({'1': 'Bán', '0': 'Mua'})
        df.columns = [camel_to_snake(col) for col in df.columns]

        df.name = self.symbol
        df.source = 'TCBS'

        if self.to_df:
            return df
        else:
            return df.to_dict(orient='records')[0]
        
    def subsidiaries (self, page_size:Optional[int]=100, page:Optional[int]=0):
        """
        Truy xuất thông tin các công ty con, công ty liên kết của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - page_size (int): Số lượng công ty con trên mỗi trang. Mặc định là 100.
            - page (int): Trang cần truy xuất thông tin. Mặc định là 0.
        """
        # If page_size is greater than 100, set it to 100, loop through the page number to get all the subsidiaries
        df_ls = []
        if page_size > 100:
            max_page = page_size // 100
            page_size = 100
            for page in range(max_page):
                try:
                    url = f"{_BASE_URL}/{_ANALYSIS_URL}/v1/company/{self.symbol}/sub-companies?page={page}&size={page_size}"
                    response = requests.request("GET", url, headers=self.headers)
                    if response.status_code != 200:
                        logger.error(f"Error fetching subsidiaries data for {self.symbol} at page {page}. Details: {response.text}")
                    df = json_normalize(response.json()['listSubCompany'])
                    df_ls.append(df)
                except:
                    logger.error(f"Error fetching subsidiaries data for {self.symbol} at page {page}. Details: {response.text}")
                    continue
        else:
            url = f"{_BASE_URL}/{_ANALYSIS_URL}/v1/company/{self.symbol}/sub-companies?page={page}&size={page_size}"
            response = requests.request("GET", url, headers=self.headers)
            if response.status_code != 200:
                logger.error(f"Error fetching subsidiaries data for {self.symbol}. Details: {response.text}")
            df = json_normalize(response.json()['listSubCompany'])
            df_ls.append(df)
        df = pd.concat(df_ls, ignore_index=True)
        try:
            df.drop(columns=['no', 'ticker'], inplace=True)
        except:
            pass
        df.rename(columns={'companyName': 'subCompanyName', 'ownPercent': 'subOwnPercent'}, inplace=True)
        df.columns = [camel_to_snake(col) for col in df.columns]

        df.name = self.symbol
        df.source = 'TCBS'

        if self.to_df:
            return df
        else:
            return df.to_dict(orient='records')[0]
        
    def officers (self, page_size:Optional[int]=20, page:Optional[int]=0):
        """
        Truy xuất danh sách lãnh đạo của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - page_size (int): Số lượng lãnh đạo trên mỗi trang. Mặc định là 20.
            - page (int): Trang cần truy xuất thông tin. Mặc định là 0.
        """
        url = f"{_BASE_URL}/{_ANALYSIS_URL}/v1/company/{self.symbol}/key-officers?page={page}&size={page_size}"
        response = requests.request("GET", url, headers=self.headers)
        if response.status_code != 200:
            logger.error(f"Error fetching officers data for {self.symbol}. Details: {response.text}")
        df = json_normalize(response.json()['listKeyOfficer'])
        
        try:
            df.drop(columns=['no', 'ticker'], inplace=True)
        except:
            pass

        df.rename(columns={'name': 'officerName', 'position': 'officerPosition', 'ownPercent':'officerOwnPercent'}, inplace=True)
        df.sort_values(by=['officerOwnPercent', 'officerPosition'], ascending=False, inplace=True)
        df.columns = [camel_to_snake(col) for col in df.columns]

        df.name = self.symbol
        df.source = 'TCBS'

        if self.to_df:
            return df
        else:
            return df.to_dict(orient='records')[0]
        
    def events (self, page_size:Optional[int]=15, page:Optional[int]=0):
        """
        Truy xuất thông tin sự kiện của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - page_size (int): Số lượng sự kiện trên mỗi trang. Mặc định là 15.
            - page (int): Trang cần truy xuất thông tin. Mặc định là 0.
        """
        url = f"{_BASE_URL}/{_ANALYSIS_URL}/v1/ticker/{self.symbol}/events-news?page={page}&size={page_size}"
        response = requests.request("GET", url, headers=self.headers)
        if response.status_code != 200:
            logger.error(f"Error fetching company events data for {self.symbol}. Details: {response.text}")
        df = pd.DataFrame(response.json()['listEventNews'])
        df.columns = [camel_to_snake(col) for col in df.columns]
        try:
            df.rename(columns={'price_change_ratio1_m':'price_change_ratio_1m', 'ex_rigth_date':'exer_right_date'}, inplace=True)
            df.drop(columns=['ticker'], inplace=True)
            df['event_desc'] = df['event_desc'].apply(lambda x: BeautifulSoup(x, 'html.parser').get_text())
            df['event_desc'] = df['event_desc'].str.replace('\n', ' ')
        except:
            pass
        df.name = self.symbol
        df.source = 'TCBS'

        if self.to_df:
            return df
        else:
            return df.to_dict(orient='records')[0]

    def news (self, page_size:Optional[int]=15, page:Optional[int]=0):
        """
        Truy xuất thông tin tin tức liên quan đến công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - page_size (int): Số lượng tin tức trên mỗi trang. Mặc định là 15.
            - page (int): Trang cần truy xuất thông tin. Mặc định là 0.
        """
        url = f"{_BASE_URL}/{_ANALYSIS_URL}/v1/ticker/{self.symbol}/activity-news?page={page}&size={page_size}"
        response = requests.request("GET", url, headers=self.headers)
        if response.status_code != 200:
            logger.error(f"Error fetching company news data for {self.symbol}. Details: {response.text}")
        df = pd.DataFrame(response.json()['listActivityNews'])
        try:
            df.drop(columns=['ticker'], inplace=True)
        except:
            pass
        df.columns = [camel_to_snake(col) for col in df.columns]
        df.rename(columns={'price_change_ratio1_m':'price_change_ratio_1m'}, inplace=True)

        df.name = self.symbol
        df.source = 'TCBS'

        if self.to_df:
            return df
        else:
            return df.to_dict(orient='records')[0]
        
    def dividends (self, page_size:Optional[int]=15, page:Optional[int]=0):
        """
        Truy xuất lịch sử cổ tức của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.
        """
        url = f'{_BASE_URL}/{_ANALYSIS_URL}/v1/company/{self.symbol}/dividend-payment-histories?page={page}&size={page_size}'
        response = requests.get(url, headers=self.headers)
        df = json_normalize(response.json()['listDividendPaymentHis'])
        try:
            df.drop(columns=['no', 'ticker'], inplace=True)
        except:
            pass
        df.columns = [camel_to_snake(col) for col in df.columns]
        df.name = self.symbol
        df.source = 'TCBS'
        if self.to_df:
            return df
        else:
            return df.to_dict(orient='records')[0]
