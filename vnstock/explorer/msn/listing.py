"""Listing module."""

from typing import Dict, Optional
from datetime import datetime
import pandas as pd
import requests
import json
# from vnstock.core.utils.parser import camel_to_snake
from vnai import optimize_execution
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers
from vnstock.explorer.msn.helper import msn_apikey
from vnstock.explorer.msn.const import _SYMBOL_INDEX_COLS_MAP

logger = get_logger(__name__)

class Listing:
    """
    Cấu hình truy cập dữ liệu lịch sử giá chứng khoán từ VCI.
    """
    def __init__(self, api_version='20250317', random_agent=False):
        self.data_source = 'MSN'
        self.headers = get_headers(data_source=self.data_source, random_agent=random_agent)
        self.apikey = msn_apikey(self.headers, version=api_version)
    
    
    @optimize_execution('MSN')
    def search_symbol_id (self, query:str, locale:Optional[str]=None, limit:Optional[int]=10, show_log:Optional[bool]=False, to_df: bool =True) -> Dict:
        """
        Truy xuất danh sách toàn. bộ mã và tên các cổ phiếu trên thị trường Việt Nam.

        Tham số:
            - query (bắt buộc): Từ khóa tìm kiếm mã cổ phiếu.
            - locale (tùy chọn): Ngôn ngữ mục tiêu, đồng thời sử dụng để lọc kết quả, ví dụ 'vi-vn', 'en-us'. Mặc định là None.
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
            - to_df (tùy chọn): Chuyển đổi dữ liệu danh sách mã cổ phiếu trả về dưới dạng DataFrame. Mặc định là True. Đặt là False để trả về dữ liệu dạng JSON.
        """
        url = f"https://services.bingapis.com/contentservices-finance.csautosuggest/api/v1/Query?query={query}&market={locale}&count={limit}"

        response = requests.request("GET", url, headers=self.headers)

        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch data: {response.status_code} - {response.reason}")

        json_data = response.json()['data']['stocks']

        if show_log:
            logger.info(f'Truy xuất thành công dữ liệu danh sách rút gọn các mã cổ phiếu cho {len(json_data["data"]["stocks"])} mã.')

        combine_ls = []
        for item in json_data:
            item_data = json.loads(item)
            combine_ls.append(item_data)

        combine_df = pd.DataFrame(combine_ls)
        select_col_names = list(_SYMBOL_INDEX_COLS_MAP.keys())
        combine_df = combine_df[select_col_names]
        combine_df.rename(columns=_SYMBOL_INDEX_COLS_MAP, inplace=True)
        
        if locale is not None:
            combine_df = combine_df[combine_df['locale'] == locale]

        if to_df:
            return combine_df
        else:
            return combine_df.to_dict(orient='records')


