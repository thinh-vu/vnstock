"""
Module quản lý các thông tin liên quan đến công ty từ nguồn dữ liệu TCBS.
"""

import pandas as pd
from pandas import json_normalize
from bs4 import BeautifulSoup
from typing import Dict, Optional, List, Union
from vnstock.core.utils import client
from vnstock.explorer.tcbs.const import _BASE_URL, _ANALYSIS_URL
from vnstock.core.utils.parser import get_asset_type, camel_to_snake
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers
from vnai import optimize_execution
from vnstock.explorer.tcbs.financial import Finance

logger = get_logger(__name__)

class Company:
    """
    Class (lớp) quản lý các thông tin liên quan đến công ty từ nguồn dữ liệu TCBS.

    Tham số:
        - symbol (str): Mã chứng khoán của công ty cần truy xuất thông tin.
        - random_agent (bool): Sử dụng user-agent ngẫu nhiên hoặc không. Mặc định là False.
        - to_df (bool): Chuyển đổi dữ liệu thành DataFrame hoặc không. Mặc định là True.
        - show_log (bool): Hiển thị thông tin log hoặc không. Mặc định là False.
    """
    def __init__(self, symbol: str, random_agent: bool = False, 
                 to_df: Optional[bool] = True, show_log: Optional[bool] = False):
        """
        Khởi tạo đối tượng Company với các tham số cho việc truy xuất dữ liệu.
        """
        self.symbol = symbol.upper()
        self.asset_type = get_asset_type(self.symbol)
        
        # Validate if symbol is a stock
        if self.asset_type not in ['stock']:
            raise ValueError("Mã chứng khoán không hợp lệ. Chỉ cổ phiếu mới có thông tin.")
            
        self.base_url = _BASE_URL
        self.headers = get_headers(data_source='TCBS', random_agent=random_agent)
        self.show_log = show_log
        self.to_df = to_df
        self.finance = Finance(self.symbol)

        # Adjust logger level based on show_log parameter
        if not self.show_log:
            logger.setLevel('CRITICAL')

    def _process_response(self, df: pd.DataFrame, exclude_columns: Optional[List[str]] = None) -> Union[pd.DataFrame, Dict]:
        """
        Helper method to process response DataFrame and return in required format.
        
        Args:
            df: DataFrame to process
            exclude_columns: Columns to exclude from DataFrame
            
        Returns:
            DataFrame or dict based on to_df setting
        """
        # Convert column names to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]
        
        # Drop specified columns if they exist
        if exclude_columns:
            for col in exclude_columns:
                if col in df.columns:
                    df.drop(columns=[col], inplace=True)
        
        # Add metadata
        df.name = self.symbol
        df.source = 'TCBS'
        
        # Return DataFrame or dict based on to_df setting
        if self.to_df:
            return df
        else:
            return df.to_dict(orient='records')[0]

    @optimize_execution("TCBS")
    def overview(self) -> Union[pd.DataFrame, Dict]:
        """
        Truy xuất thông tin tổng quan của mã chứng khoán từ nguồn dữ liệu TCBS với các thông số cài đặt khi khởi tạo class.
        
        Returns:
            Thông tin tổng quan dưới dạng DataFrame hoặc dict.
        """
        url = f'{self.base_url}/{_ANALYSIS_URL}/v1/ticker/{self.symbol}/overview'
        
        # Use centralized request handler
        data = client.send_request(
            url=url,
            headers=self.headers,
            method="GET",
            show_log=self.show_log
        )
        
        # Process response data
        df = pd.DataFrame(data, index=[0])
        
        # Select relevant columns
        df = df[['ticker', 'exchange', 'industry', 'companyType',
                'noShareholders', 'foreignPercent', 'outstandingShare', 'issueShare',
                'establishedYear', 'noEmployees',  
                'stockRating', 'deltaInWeek', 'deltaInMonth', 'deltaInYear', 
                'shortName', 'website', 'industryID', 'industryIDv2']]
                
        # Convert column names to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]
        
        # Rename specific columns
        df.rename(columns={
            'industry_i_dv2': 'industry_id_v2', 
            'ticker': 'symbol'
        }, inplace=True)

        return self._process_response(df)
    
    @optimize_execution("TCBS")
    def profile(self) -> Union[pd.DataFrame, Dict]:
        """
        Truy xuất thông tin mô tả công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.
        
        Returns:
            Thông tin mô tả công ty dưới dạng DataFrame hoặc dict.
        """
        url = f"{self.base_url}/{_ANALYSIS_URL}/v1/company/{self.symbol}/overview"
        
        # Use centralized request handler
        response_data = client.send_request(
            url=url,
            headers=self.headers,
            method="GET",
            show_log=self.show_log
        )
        
        # Process response data
        df = json_normalize(response_data)
        
        # Clean HTML content in text fields
        for col in df.columns:
            try:
                df[col] = df[col].apply(lambda x: BeautifulSoup(x, 'html.parser').get_text())
                df[col] = df[col].str.replace('\n', ' ')
            except:
                pass
                    
        # Add symbol column
        df['symbol'] = self.symbol
        
        # Drop unnecessary columns
        try:
            df.drop(columns=['id', 'ticker'], inplace=True, errors='ignore')
        except:
            pass
        
        # Convert column names to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]
        
        # Reorder columns to put symbol first
        cols = df.columns.tolist()
        cols.remove('symbol')
        cols = ['symbol'] + cols
        df = df[cols]
        
        # Add metadata
        df.name = self.symbol
        df.source = 'TCBS'
        
        # Return in requested format
        if self.to_df:
            return df
        else:
            return df.to_dict(orient='records')[0]

    @optimize_execution("TCBS")
    def shareholders(self) -> Union[pd.DataFrame, Dict]:
        """
        Truy xuất thông tin cổ đông lớn của công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.
        
        Returns:
            Thông tin cổ đông lớn dưới dạng DataFrame hoặc dict.
        """
        url = f"{self.base_url}/{_ANALYSIS_URL}/v1/company/{self.symbol}/large-share-holders"
        
        # Use centralized request handler
        response_data = client.send_request(
            url=url,
            headers=self.headers,
            method="GET",
            show_log=self.show_log
        )
        
        # Process response data
        df = json_normalize(response_data['listShareHolder'])
        
        # Rename columns for clarity
        df.rename(columns={
            'name': 'shareHolder', 
            'ownPercent': 'shareOwnPercent'
        }, inplace=True)

        return self._process_response(df, exclude_columns=['no', 'ticker'])
        
    @optimize_execution("TCBS")
    def insider_deals(self, page_size: Optional[int] = 20, page: Optional[int] = 0) -> Union[pd.DataFrame, Dict]:
        """
        Truy xuất thông tin giao dịch nội bộ của công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - page_size (int): Số lượng giao dịch trên mỗi trang. Mặc định là 20.
            - page (int): Trang cần truy xuất thông tin. Mặc định là 0.
            
        Returns:
            Thông tin giao dịch nội bộ dưới dạng DataFrame hoặc dict.
        """
        url = f"{self.base_url}/{_ANALYSIS_URL}/v1/company/{self.symbol}/insider-dealing"
        
        # Use centralized request handler
        response_data = client.send_request(
            url=url,
            headers=self.headers,
            method="GET",
            params={"page": page, "size": page_size},
            show_log=self.show_log
        )
        
        # Process response data
        try:
            df = json_normalize(response_data['listInsiderDealing'])
        except KeyError:
            logger.error(f"No insider dealing data available for {self.symbol}")
            return pd.DataFrame() if self.to_df else {}
            
        # Drop unnecessary columns
        try:
            df.drop(columns=['no', 'ticker'], inplace=True, errors='ignore')
        except KeyError as e:
            logger.warning(f"Columns to drop not found: {e}")

        # Rename columns for clarity
        try:
            df.rename(columns={
                'anDate': 'dealAnnounceDate', 
                'dealingMethod': 'dealMethod', 
                'dealingAction': 'dealAction', 
                'quantity': 'dealQuantity', 
                'price': 'dealPrice', 
                'ratio': 'dealRatio'
            }, inplace=True)
        except KeyError as e:
            logger.error(f"Error renaming columns: {e}")

        # Format date and sort
        if 'dealAnnounceDate' in df.columns:
            df['dealAnnounceDate'] = pd.to_datetime(df['dealAnnounceDate'], format='%d/%m/%y')
            df.sort_values(by='dealAnnounceDate', ascending=False, inplace=True)
        else:
            logger.error(f"'dealAnnounceDate' column not found in DataFrame for {self.symbol}")
            return pd.DataFrame() if self.to_df else {}

        # Map numerical codes to descriptive values
        if 'dealMethod' in df.columns:
            df['dealMethod'] = df['dealMethod'].replace({
                1: 'Cổ đông lớn', 
                2: 'Cổ đông sáng lập', 
                0: 'Cổ đông nội bộ'
            })
            
        if 'dealAction' in df.columns:
            df['dealAction'] = df['dealAction'].replace({'1': 'Bán', '0': 'Mua'})

        return self._process_response(df)
        
    @optimize_execution("TCBS")
    def subsidiaries(self, page_size: Optional[int] = 100, page: Optional[int] = 0) -> Union[pd.DataFrame, Dict]:
        """
        Truy xuất thông tin các công ty con, công ty liên kết của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - page_size (int): Số lượng công ty con trên mỗi trang. Mặc định là 100.
            - page (int): Trang cần truy xuất thông tin. Mặc định là 0.
            
        Returns:
            Thông tin công ty con dưới dạng DataFrame hoặc dict.
        """
        url = f"{self.base_url}/{_ANALYSIS_URL}/v1/company/{self.symbol}/sub-companies"
        df_list = []
        
        # Handle pagination for large result sets
        if page_size > 100:
            max_pages = (page_size + 99) // 100  # Ceiling division
            effective_page_size = 100
            
            for current_page in range(page, page + max_pages):
                try:
                    # Use centralized request handler for each page
                    response_data = client.send_request(
                        url=url,
                        headers=self.headers,
                        method="GET",
                        params={"page": current_page, "size": effective_page_size},
                        show_log=self.show_log
                    )
                    
                    page_df = json_normalize(response_data['listSubCompany'])
                    df_list.append(page_df)
                except Exception as e:
                    logger.error(f"Error fetching subsidiaries data for {self.symbol} at page {current_page}: {str(e)}")
                    continue
        else:
            # Use centralized request handler for single page
            response_data = client.send_request(
                url=url,
                headers=self.headers,
                method="GET",
                params={"page": page, "size": page_size},
                show_log=self.show_log
            )
            
            df_list.append(json_normalize(response_data['listSubCompany']))
            
        # Combine results from all pages
        if not df_list:
            return pd.DataFrame() if self.to_df else {}
            
        df = pd.concat(df_list, ignore_index=True)
        
        # Rename columns for clarity
        df.rename(columns={
            'companyName': 'subCompanyName', 
            'ownPercent': 'subOwnPercent'
        }, inplace=True)

        return self._process_response(df, exclude_columns=['no', 'ticker'])
        
    @optimize_execution("TCBS")
    def officers(self, page_size: Optional[int] = 20, page: Optional[int] = 0) -> Union[pd.DataFrame, Dict]:
        """
        Truy xuất danh sách lãnh đạo của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - page_size (int): Số lượng lãnh đạo trên mỗi trang. Mặc định là 20.
            - page (int): Trang cần truy xuất thông tin. Mặc định là 0.
            
        Returns:
            Thông tin lãnh đạo dưới dạng DataFrame hoặc dict.
        """
        url = f"{self.base_url}/{_ANALYSIS_URL}/v1/company/{self.symbol}/key-officers"
        
        # Use centralized request handler
        response_data = client.send_request(
            url=url,
            headers=self.headers,
            method="GET",
            params={"page": page, "size": page_size},
            show_log=self.show_log
        )
        
        # Process response data
        df = json_normalize(response_data['listKeyOfficer'])
        
        # Rename columns for clarity
        df.rename(columns={
            'name': 'officerName', 
            'position': 'officerPosition', 
            'ownPercent': 'officerOwnPercent'
        }, inplace=True)
        
        # Sort by ownership percentage and position
        df.sort_values(by=['officerOwnPercent', 'officerPosition'], ascending=False, inplace=True)

        return self._process_response(df, exclude_columns=['no', 'ticker'])
        
    @optimize_execution("TCBS")
    def events(self, page_size: Optional[int] = 15, page: Optional[int] = 0) -> Union[pd.DataFrame, Dict]:
        """
        Truy xuất thông tin sự kiện của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - page_size (int): Số lượng sự kiện trên mỗi trang. Mặc định là 15.
            - page (int): Trang cần truy xuất thông tin. Mặc định là 0.
            
        Returns:
            Thông tin sự kiện dưới dạng DataFrame hoặc dict.
        """
        url = f"{self.base_url}/{_ANALYSIS_URL}/v1/ticker/{self.symbol}/events-news"
        
        # Use centralized request handler
        response_data = client.send_request(
            url=url,
            headers=self.headers,
            method="GET",
            params={"page": page, "size": page_size},
            show_log=self.show_log
        )
        
        # Process response data
        df = pd.DataFrame(response_data['listEventNews'])
        
        # Convert column names to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]
        
        # Rename specific columns and process HTML content
        try:
            df.rename(columns={
                'price_change_ratio1_m': 'price_change_ratio_1m', 
                'ex_rigth_date': 'exer_right_date'
            }, inplace=True)
            
            # Process HTML in event descriptions
            try:
                df['event_desc'] = df['event_desc'].apply(lambda x: BeautifulSoup(x, 'html.parser').get_text())
                df['event_desc'] = df['event_desc'].str.replace('\n', ' ')
            except Exception as e:
                logger.warning(f"Error parsing HTML for event_desc: {e}")
                
        except Exception as e:
            logger.warning(f"Error processing event data: {e}")

        df = self._process_response(df, exclude_columns=['ticker'])
        
        # convert date columns from object to standard datetime string YYYY-mm-dd if they exist
        date_columns = ['notify_date', 'exer_date', 'reg_final_date', 'exer_right_date']
        for col in date_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], format='%Y-%m-%d %H:%M:%S').dt.strftime('%Y-%m-%d')
                except Exception as e:
                    logger.warning(f"Không thể chuyển đổi cột {col}: {str(e)}")

        return df

    @optimize_execution("TCBS")
    def news (self, page_size: Optional[int] = 15, page: Optional[int] = 0) -> Union[pd.DataFrame, Dict]:
        """
        Truy xuất thông tin tin tức liên quan đến công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.

        Tham số:
            - page_size (int): Số lượng tin tức trên mỗi trang. Mặc định là 15.
            - page (int): Trang cần truy xuất thông tin. Mặc định là 0.
            
        Returns:
            Thông tin tin tức dưới dạng DataFrame hoặc dict.
        """
        url = f"{self.base_url}/{_ANALYSIS_URL}/v1/ticker/{self.symbol}/activity-news"
        
        # Use centralized request handler
        response_data = client.send_request(
            url=url,
            headers=self.headers,
            method="GET",
            params={"page": page, "size": page_size},
            show_log=self.show_log
        )
        
        # Process response data
        df = pd.DataFrame(response_data['listActivityNews'])
        
        # Convert column names to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]
        
        # Rename specific columns
        df.rename(columns={
            'price_change_ratio1_m': 'price_change_ratio_1m'
        }, inplace=True)

        return self._process_response(df, exclude_columns=['ticker'])
        
    @optimize_execution("TCBS")
    def dividends(self, page_size: Optional[int] = 15, page: Optional[int] = 0) -> Union[pd.DataFrame, Dict]:
        """
        Truy xuất lịch sử cổ tức của một công ty theo mã chứng khoán từ nguồn dữ liệu TCBS.
        
        Tham số:
            - page_size (int): Số lượng kết quả trên mỗi trang. Mặc định là 15.
            - page (int): Trang cần truy xuất thông tin. Mặc định là 0.
            
        Returns:
            Lịch sử cổ tức dưới dạng DataFrame hoặc dict.
        """
        url = f'{self.base_url}/{_ANALYSIS_URL}/v1/company/{self.symbol}/dividend-payment-histories'
        
        # Use centralized request handler
        response_data = client.send_request(
            url=url,
            headers=self.headers,
            method="GET",
            params={"page": page, "size": page_size},
            show_log=self.show_log
        )
        
        # Process response data
        df = json_normalize(response_data['listDividendPaymentHis'])

        df = self._process_response(df, exclude_columns=['no', 'ticker'])

        # convert df['exeexercise_date'] from object in dd/mm/YY to standard datetime string YYYY-mm-dd
        df['exercise_date'] = pd.to_datetime(df['exercise_date'], format='%d/%m/%y').dt.strftime('%Y-%m-%d')

        return df

