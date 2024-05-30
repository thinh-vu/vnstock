"""Listing module."""

# Đồ thị giá, đồ thị dư mua dư bán, đồ thị mức giá vs khối lượng, thống kê hành vi thị tường
from typing import Dict, Optional
from datetime import datetime
from .const import _GROUP_CODE
import pandas as pd
import requests
from vnstock3.core.utils.parser import camel_to_snake
from vnstock3.core.utils.logger import get_logger
from vnstock3.core.utils.user_agent import get_headers

logger = get_logger(__name__)

class Listing:
    """
    Cấu hình truy cập dữ liệu lịch sử giá chứng khoán từ VCI.
    """
    def __init__(self, random_agent=False):
        self.data_source = 'VCI'
        self.headers = get_headers(data_source=self.data_source, random_agent=random_agent)
    
    def all_symbols (self, show_log:Optional[bool]=False, to_df:Optional[bool]=True) -> Dict:
        """
        Truy xuất danh sách toàn. bộ mã và tên các cổ phiếu trên thị trường Việt Nam.

        Tham số:
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
            - to_df (tùy chọn): Chuyển đổi dữ liệu danh sách mã cổ phiếu trả về dưới dạng DataFrame. Mặc định là True. Đặt là False để trả về dữ liệu dạng JSON.
        """
        url = 'https://ai.vietcap.com.vn/api/get_all_tickers'
        response = requests.request("GET", url, headers=self.headers)

        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch data: {response.status_code} - {response.reason}")

        json_data = response.json()

        if show_log:
            logger.info(f'Truy xuất thành công dữ liệu danh sách rút gọn các mã cổ phiếu cho {json_data["record_count"]} mã.')

        df = pd.DataFrame(json_data['ticker_info'])

        if to_df:
            if not json_data:
                raise ValueError("JSON data is empty or not provided.")
            # Set metadata attributes
            df.source = "VCI"
            return df
        else:
            json_data = df.to_json(orient='records')
            return json_data
        
    def symbols_by_industries (self, show_log:Optional[bool]=False, to_df:Optional[bool]=True):
        """
        Truy xuất thông tin niêm yết theo ngành (icb) của các mã cổ phiếu trên thị trường Việt Nam.

        Tham số:
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
            - to_df (tùy chọn): Chuyển đổi dữ liệu danh sách mã cổ phiếu trả về dưới dạng DataFrame. Mặc định là True. Đặt là False để trả về dữ liệu dạng JSON.
        """
        url = 'https://api.vietcap.com.vn/data-mt/graphql'

        payload = "{\"query\":\"{\\n  CompaniesListingInfo {\\n    ticker\\n    organName\\n    enOrganName\\n    icbName3\\n    enIcbName3\\n    icbName2\\n    enIcbName2\\n    icbName4\\n    enIcbName4\\n    comTypeCode\\n    icbCode1\\n    icbCode2\\n    icbCode3\\n    icbCode4\\n    __typename\\n  }\\n}\\n\",\"variables\":{}}"
        response = requests.request("POST", url, headers=self.headers, data=payload)

        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch data: {response.status_code} - {response.reason}")

        json_data = response.json()

        if show_log:
            logger.info(f'Truy xuất thành công dữ liệu danh sách cổ phiếu theo phân ngành icb.')

        df = pd.DataFrame(json_data['data']['CompaniesListingInfo'])

        if to_df:
            if not json_data:
                raise ValueError("JSON data is empty or not provided.")
            df.drop(columns=['__typename'], inplace=True)
            # apply camel_to_snake function to column names
            df.columns = [camel_to_snake(col) for col in df.columns]
            # rename ticker to symbol
            df.rename(columns={'ticker': 'symbol'}, inplace=True)
            # Set metadata attributes
            df.source = "VCI"
            return df
        else:
            json_data = df.to_json(orient='records')
            return json_data
        
    def symbols_by_exchange(self, show_log:Optional[bool]=False, to_df:Optional[bool]=True):
        """
        Truy xuất thông tin niêm yết theo sàn của các mã cổ phiếu trên thị trường Việt Nam.

        Tham số:
                - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
                - to_df (tùy chọn): Chuyển đổi dữ liệu danh sách mã cổ phiếu trả về dưới dạng DataFrame. Mặc định là True. Đặt là False để trả về dữ liệu dạng JSON.
        """
        url = 'https://mt.vietcap.com.vn/api/price/symbols/getAll'
        response = requests.request("GET", url, headers=self.headers)

        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch data: {response.status_code} - {response.reason}")

        json_data = response.json()

        if show_log:
            logger.info(f'Truy xuất thành công dữ liệu danh sách cổ phiếu theo sàn.')

        df = pd.DataFrame(json_data)

        if to_df:
            if not json_data:
                raise ValueError("JSON data is empty or not provided.")
            # apply camel_to_snake function to column names
            df.columns = [camel_to_snake(col) for col in df.columns]
            # rename ticker to symbol
            df.rename(columns={'ticker': 'symbol', 'board':'exchange'}, inplace=True)
            # rearrange symbol column to the first
            cols = df.columns.tolist()
            # remove symbol from the list
            cols.remove('symbol')
            # insert symbol at the first position
            cols.insert(0, 'symbol')
            # reorder the columns
            df = df[cols]
            # Set metadata attributes
            df.source = "VCI"
            return df
        else:
            json_data = df.to_json(orient='records')
            return json_data
        
    def industries_icb (self, show_log:Optional[bool]=False, to_df:Optional[bool]=True):
        """
        Truy xuất thông tin phân ngành icb của các mã cổ phiếu trên thị trường Việt Nam.

        Tham số:
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
            - to_df (tùy chọn): Chuyển đổi dữ liệu danh sách mã cổ phiếu trả về dưới dạng DataFrame. Mặc định là True. Đặt là False để trả về dữ liệu dạng JSON.
        """
        url = 'https://api.vietcap.com.vn/data-mt/graphql'
        payload = "{\"query\":\"query Query {\\n  ListIcbCode {\\n    icbCode\\n    level\\n    icbName\\n    enIcbName\\n    __typename\\n  }\\n  CompaniesListingInfo {\\n    ticker\\n    icbCode1\\n    icbCode2\\n    icbCode3\\n    icbCode4\\n    __typename\\n  }\\n}\",\"variables\":{}}"
        response = requests.request("POST", url, headers=self.headers, data=payload)

        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch data: {response.status_code} - {response.reason}")

        json_data = response.json()

        if show_log:
            logger.info(f'Truy xuất thành công dữ liệu danh sách phân ngành icb.')

        df = pd.DataFrame(json_data['data']['ListIcbCode'])

        if to_df:
            if not json_data:
                raise ValueError("JSON data is empty or not provided.")
            df.drop(columns=['__typename'], inplace=True)
            # apply camel_to_snake function to column names
            column_order = ['icbName', 'enIcbName', 'icbCode', 'level']
            df = df[column_order]
            df.columns = [camel_to_snake(col) for col in df.columns]
            # Set metadata attributes
            df.source = "VCI"
            return df
        else:
            json_data = df.to_json(orient='records')
            return json_data
        
    def symbols_by_group (self, group: str ='VN30', show_log:Optional[bool]=False, to_df:Optional[bool]=True):
        """
        Truy xuất danh sách các mã cổ phiếu theo tên nhóm trên thị trường Việt Nam.

        Tham số:
            - group (tùy chọn): Tên nhóm cổ phiếu. Mặc định là 'VN30'. Các mã có thể là: HOSE, VN30, VNMidCap, VNSmallCap, VNAllShare, VN100, ETF, HNX, HNX30, HNXCon, HNXFin, HNXLCap, HNXMSCap, HNXMan, UPCOM, FU_INDEX (mã chỉ số hợp đồng tương lai), CW (chứng quyền).
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
            - to_df (tùy chọn): Chuyển đổi dữ liệu danh sách mã cổ phiếu trả về dưới dạng DataFrame. Mặc định là True. Đặt là False để trả về dữ liệu dạng JSON.
        """
        if group not in _GROUP_CODE:
            raise ValueError(f"Invalid group. Group must be in {_GROUP_CODE}")
        url = f'https://mt.vietcap.com.vn/api/price/symbols/getByGroup?group={group}'
        
        response = requests.request("GET", url, headers=self.headers)

        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch data: {response.status_code} - {response.reason}")

        json_data = response.json()

        if show_log:
            logger.info(f'Truy xuất thành công dữ liệu danh sách mã CP theo nhóm.')

        df = pd.DataFrame(json_data)

        if to_df:
            if not json_data:
                raise ValueError("JSON data is empty or not provided.")
            # Set metadata attributes
            df.source = "VCI"
            return df['symbol']
        else:
            json_data = df.to_json(orient='records')
            return json_data

    def all_future_indices (self, show_log:Optional[bool]=False, to_df:Optional[bool]=True):
        return self.symbols_by_group(group='FU_INDEX', show_log=show_log, to_df=to_df)
    
    def all_government_bonds (self, show_log:Optional[bool]=False, to_df:Optional[bool]=True):
        return self.symbols_by_group(group='FU_BOND', show_log=show_log, to_df=to_df)
    
    def all_covered_warrant (self, show_log:Optional[bool]=False, to_df:Optional[bool]=True):
        return self.symbols_by_group(group='CW', show_log=show_log, to_df=to_df)
    
    def all_bonds (self, show_log:Optional[bool]=False, to_df:Optional[bool]=True):
        return self.symbols_by_group(group='BOND', show_log=show_log, to_df=to_df)


