"""Listing module."""

from typing import Optional
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
    Cấu hình truy cập dữ liệu lịch sử giá chứng khoán từ MSN.
    Configure access to historical stock price data from MSN.
    """
    def __init__(self, api_version='20250317', random_agent=False):
        self.data_source = 'MSN'
        self.headers = get_headers(data_source=self.data_source, random_agent=random_agent)
        self.apikey = msn_apikey(self.headers, version=api_version)
    
    
    @optimize_execution('MSN')
    def search_symbol_id(self, query: str, locale: Optional[str] = None, 
                        limit: Optional[int] = 10, 
                        show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Truy xuất danh sách toàn bộ mã và tên các cổ phiếu từ thị trường.
        Retrieve the list of all stock symbols and names from the market.

        Args:
            - query (required): Từ khóa tìm kiếm mã cổ phiếu (Keyword to search for stock symbols).
            - locale (optional): Ngôn ngữ mục tiêu, đồng thời sử dụng để lọc kết quả. Mặc định là None (Target language, also used to filter results, e.g., 'vi-vn', 'en-us'. Default is None).
            - limit (optional): Giới hạn số kết quả. Mặc định là 10 (Limit number of results. Default is 10).
            - show_log (optional): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False (Show log info for debugging. Default is False).
        """
        url = f"https://services.bingapis.com/contentservices-finance.csautosuggest/api/v1/Query?query={query}&market={locale}&count={limit}"

        response = requests.request("GET", url, headers=self.headers)

        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch data: {response.status_code} - {response.reason}")

        json_data = response.json()['data']['stocks']

        if show_log:
            logger.info(f'Truy xuất thành công dữ liệu danh sách rút gọn các mã cổ phiếu cho {len(json_data)} mã.')

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

        return combine_df
    @optimize_execution('MSN')
    def search_symbol(self, query: str, locale: Optional[str] = None, 
                        limit: Optional[int] = 10, 
                        show_log: Optional[bool] = False) -> pd.DataFrame:
        """Alias for search_symbol_id for registry compatibility."""
        return self.search_symbol_id(query=query, locale=locale, limit=limit, show_log=show_log)

    @optimize_execution('MSN')
    def info(self, query: str, locale: Optional[str] = None, 
                        limit: Optional[int] = 10, 
                        show_log: Optional[bool] = False) -> pd.DataFrame:
        """Alias for search_symbol_id to retrieve detailed asset info."""
        return self.search_symbol_id(query=query, locale=locale, limit=limit, show_log=show_log)


# Register provider
from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401
ProviderRegistry.register('listing', 'msn', Listing)
