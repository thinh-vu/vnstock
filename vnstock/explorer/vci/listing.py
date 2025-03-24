"""Listing module."""

# Đồ thị giá, đồ thị dư mua dư bán, đồ thị mức giá vs khối lượng, thống kê hành vi thị tường
from typing import Dict, Optional
from datetime import datetime
from .const import _GROUP_CODE, _TRADING_URL, _GRAPHQL_URL
import json
import requests
import pandas as pd
from vnstock.core.utils.parser import camel_to_snake
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers
from vnstock.core.utils.client import send_request
from vnstock.core.utils.transform import drop_cols_by_pattern, reorder_cols
from vnai import optimize_execution
logger = get_logger(__name__)

class Listing:
    """
    Cấu hình truy cập dữ liệu lịch sử giá chứng khoán từ VCI.
    """
    def __init__(self, random_agent:Optional[bool]=False, show_log:Optional[bool]=False):
        self.data_source = 'VCI'
        self.base_url = _TRADING_URL
        self.headers = get_headers(data_source=self.data_source, random_agent=random_agent)
        self.show_log = show_log
        if not show_log:
            logger.setLevel('CRITICAL')

    @optimize_execution("VCI")
    def all_symbols (self, show_log:Optional[bool]=False, to_df:Optional[bool]=True) -> Dict:
        """
        Truy xuất danh sách toàn. bộ mã và tên các cổ phiếu trên thị trường Việt Nam.

        Tham số:
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
            - to_df (tùy chọn): Chuyển đổi dữ liệu danh sách mã cổ phiếu trả về dưới dạng DataFrame. Mặc định là True. Đặt là False để trả về dữ liệu dạng JSON.
        """
        df = self.symbols_by_exchange(show_log=show_log, to_df=True)
        df = df.query('type == "STOCK"').reset_index(drop=True)
        df = df[['symbol', 'organ_name']]

        if to_df:
            return df
        else:
            json_data = df.to_json(orient='records')
            return json_data
        
    @optimize_execution("VCI")
    def symbols_by_industries (self, lang:str='vi', show_log: Optional[bool]=False, to_df:Optional[bool]=True):
        """
        Truy xuất thông tin phân ngành icb của các mã cổ phiếu trên thị trường Việt Nam.

        Tham số:
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
            - to_df (tùy chọn): Chuyển đổi dữ liệu danh sách mã cổ phiếu trả về dưới dạng DataFrame. Mặc định là True. Đặt là False để trả về dữ liệu dạng JSON.
        """
        if lang not in ['vi', 'en']:
            raise ValueError("Tham số lang phải là 'vi' hoặc 'en'.")

        payload = "{\"query\":\"{\\n  CompaniesListingInfo {\\n    ticker\\n    organName\\n    enOrganName\\n    icbName3\\n    enIcbName3\\n    icbName2\\n    enIcbName2\\n    icbName4\\n    enIcbName4\\n    comTypeCode\\n    icbCode1\\n    icbCode2\\n    icbCode3\\n    icbCode4\\n    __typename\\n  }\\n}\\n\",\"variables\":{}}"
        payload = json.loads(payload)

        # Use the send_request utility from api_client
        json_data = send_request(
            url=_GRAPHQL_URL, 
            headers=self.headers, 
            method="POST", 
            payload=payload,
            show_log=show_log
        )

        if not json_data:
            raise ValueError("Không tìm thấy dữ liệu. Vui lòng kiểm tra lại.")

        if show_log:
            logger.info(f'Truy xuất thành công dữ liệu danh sách phân ngành icb.')

        df = pd.DataFrame(json_data['data']['CompaniesListingInfo'])
        df.columns = [camel_to_snake(col) for col in df.columns]
        df = df.drop(columns=['__typename'])
        df = df.rename(columns={'ticker': 'symbol'})
        df.source = "VCI"

        if lang == 'vi':
            df = drop_cols_by_pattern(df, ['en_'])
        else:
            df = df.drop(columns=['organ_name', 'icb_name2', 'icb_name3', 'icb_name4'])
            # rename columns for those contain 'en_' with 'en_' removed
            df.columns = [col.replace('en_', '') for col in df.columns]

        if to_df:
            return df
        else:
            json_data = df.to_json(orient='records')
            return json_data

    @optimize_execution("VCI")
    def symbols_by_exchange(self, lang:str='vi', show_log:Optional[bool]=False, to_df:Optional[bool]=True):
        """
        Truy xuất thông tin niêm yết theo sàn của các mã cổ phiếu trên thị trường Việt Nam.

        Tham số:
                - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
                - to_df (tùy chọn): Chuyển đổi dữ liệu danh sách mã cổ phiếu trả về dưới dạng DataFrame. Mặc định là True. Đặt là False để trả về dữ liệu dạng JSON.
        """
        if lang not in ['vi', 'en']:
            raise ValueError("Tham số lang phải là 'vi' hoặc 'en'.")

        url = self.base_url + '/price/symbols/getAll'
        
        # Use the send_request utility from api_client
        json_data = send_request(
            url=url, 
            headers=self.headers, 
            method="GET", 
            payload=None,
            show_log=show_log
        )

        if not json_data:
            raise ValueError("Không tìm thấy dữ liệu. Vui lòng kiểm tra lại.")

        if show_log:
            logger.info(f'Truy xuất dữ liệu thành công cho {len(json_data)} mã.')

        df = pd.DataFrame(json_data)

        df.columns = [camel_to_snake(col) for col in df.columns]
        df = df.rename(columns={'board': 'exchange'})
        df = reorder_cols(df, ['symbol', 'exchange', 'type'], position='first')
        df = df.drop(columns=['id'])

        if lang == 'vi':
            df = drop_cols_by_pattern(df, ['en_'])
        else:
            df = df.drop(columns=['organ_name', 'organ_short_name'])
            # rename columns for those contain 'en_' with 'en_' removed
            df.columns = [col.replace('en_', '') for col in df.columns]

        if to_df:
            # Set metadata attributes
            df.source = "VCI"
            return df
        else:
            json_data = df.to_json(orient='records')
            return json_data

    @optimize_execution("VCI")
    def industries_icb (self, show_log: Optional[bool]=False, to_df:Optional[bool]=True):
        """
        Truy xuất thông tin phân ngành icb của các mã cổ phiếu trên thị trường Việt Nam.

        Tham số:
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
            - to_df (tùy chọn): Chuyển đổi dữ liệu danh sách mã cổ phiếu trả về dưới dạng DataFrame. Mặc định là True. Đặt là False để trả về dữ liệu dạng JSON.
        """
        payload = "{\"query\":\"query Query {\\n  ListIcbCode {\\n    icbCode\\n    level\\n    icbName\\n    enIcbName\\n    __typename\\n  }\\n  CompaniesListingInfo {\\n    ticker\\n    icbCode1\\n    icbCode2\\n    icbCode3\\n    icbCode4\\n    __typename\\n  }\\n}\",\"variables\":{}}"
        payload = json.loads(payload)

        # Use the send_request utility from api_client
        json_data = send_request(
            url=_GRAPHQL_URL, 
            headers=self.headers, 
            method="POST", 
            payload=payload,
            show_log=show_log
        )

        if not json_data:
            raise ValueError("Không tìm thấy dữ liệu. Vui lòng kiểm tra lại.")

        if show_log:
            logger.info(f'Truy xuất thành công dữ liệu danh sách phân ngành icb.')

        df = pd.DataFrame(json_data['data']['ListIcbCode'])
        df.columns = [camel_to_snake(col) for col in df.columns]
        df = df.drop(columns=['__typename'])
        df =  df[['icb_name', 'en_icb_name', 'icb_code', 'level']]
        df.source = "VCI"

        if to_df:
            return df
        else:
            json_data = df.to_json(orient='records')
            return json_data

    @optimize_execution("VCI")
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
        
        url = self.base_url + f'/price/symbols/getByGroup?group={group}'

        # Use the send_request utility from api_client
        json_data = send_request(
            url=url, 
            headers=self.headers, 
            method="GET", 
            payload=None,
            show_log=show_log
        )

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

    @optimize_execution("VCI")
    def all_future_indices (self, show_log:Optional[bool]=False, to_df:Optional[bool]=True):
        return self.symbols_by_group(group='FU_INDEX', show_log=show_log, to_df=to_df)

    @optimize_execution("VCI")
    def all_government_bonds (self, show_log:Optional[bool]=False, to_df:Optional[bool]=True):
        return self.symbols_by_group(group='FU_BOND', show_log=show_log, to_df=to_df)

    @optimize_execution("VCI")
    def all_covered_warrant (self, show_log:Optional[bool]=False, to_df:Optional[bool]=True):
        return self.symbols_by_group(group='CW', show_log=show_log, to_df=to_df)

    @optimize_execution("VCI")
    def all_bonds (self, show_log:Optional[bool]=False, to_df:Optional[bool]=True):
        return self.symbols_by_group(group='BOND', show_log=show_log, to_df=to_df)


