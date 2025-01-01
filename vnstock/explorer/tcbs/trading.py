# Các thông tin về giao dịch, sở hữu của các bên (đối tượng tham gia thị trường)

import requests
import pandas as pd
from typing import Optional
# from datetime import datetime
from .const import _BASE_URL, _STOCKS_URL, _PRICE_BOARD_COLS_MAP, _PRICE_BOARD_STD_COLS, _PRICE_BOARD_EXT_COLS
from vnstock.core.utils.parser import get_asset_type
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers

logger = get_logger(__name__)


class Trading:
    """
    Truy xuất dữ liệu giao dịch của mã chứng khoán từ nguồn dữ liệu TCBS.
    """
    def __init__(self, symbol:Optional[str], random_agent=False, show_log:Optional[bool]=True):
        self.symbol = symbol.upper()
        self.asset_type = get_asset_type(self.symbol)
        self.show_log = show_log
        self.base_url = _BASE_URL
        self.headers = get_headers(data_source='TCBS', random_agent=random_agent)

        if not show_log:
            logger.setLevel('CRITICAL')
        
    def price_board (self, symbol_ls:list, std_columns: Optional[bool]=True, to_df: Optional[bool]=True, show_log: bool=False):
        """
        This function returns the trading price board of a target stocks list.
        Args:
            symbol_ls (:obj:`str`, required): STRING list of symbols separated by "," without any space. Ex: "TCB,SSI,BID"
        """ 
        symbols = ",".join(symbol_ls)
        url = f'{self.base_url}/{_STOCKS_URL}/v1/stock/second-tc-price?tickers={symbols}'
        response = requests.get(url, headers=self.headers)
        if show_log:
            logger.info(f'Requested URL: {url}')
        if response.status_code != 200:
            raise ConnectionError(f"Tải dữ liệu không thành công: {response.status_code} - {response.reason}")
        data = response.json()['data']
        df = pd.DataFrame(data)
        if show_log:
            logger.info(f"Data:\n {data}")
        # drop columns named seq
        df.drop(columns=['seq'], inplace=True)
        
        if std_columns:
            df = df[_PRICE_BOARD_STD_COLS]
        else:
            df = df[_PRICE_BOARD_EXT_COLS]

        df = df.rename(columns=_PRICE_BOARD_COLS_MAP)
        df.source = 'TCBS'

        if to_df:
            return df
        else:
            json_data = df.to_json(orient='records')
            return json_data