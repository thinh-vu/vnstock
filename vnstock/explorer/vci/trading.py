# Các thông tin về giao dịch, sở hữu của các bên (đối tượng tham gia thị trường)

from typing import List, Dict, Optional, Union
from datetime import datetime
from .const import _TRADING_URL
import json
import requests
import pandas as pd
from vnai import optimize_execution
from vnstock.core.utils.parser import get_asset_type, camel_to_snake, flatten_data
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers
from vnstock.core.utils.transform import flatten_hierarchical_index
logger = get_logger(__name__)


class Trading:
    """
    Truy xuất dữ liệu giao dịch của mã chứng khoán từ nguồn dữ liệu VCI.
    """
    def __init__(self, symbol:Optional[str]='VCI', random_agent=False, show_log:Optional[bool]=True):
        self.symbol = symbol.upper()
        self.asset_type = get_asset_type(self.symbol)
        self.base_url = _TRADING_URL
        self.headers = get_headers(data_source='VCI', random_agent=random_agent)
        self.show_log = show_log

        if not show_log:
            logger.setLevel('CRITICAL')

    @optimize_execution("VCI")
    def price_board (self, symbols_list: List[str], 
                     to_df:Optional[bool]=True, 
                     show_log:Optional[bool]=False,
                     flatten_columns:Optional[bool]=False,
                     separator:Optional[str]='_',
                     drop_levels:Optional[Union[int, List[int]]]=None):
        """
        Truy xuất thông tin bảng giá của các mã chứng khoán tuỳ chọn từ nguồn dữ liệu VCI.
        """
        url = f'{self.base_url}price/symbols/getList'
        payload = json.dumps({"symbols": symbols_list})

        if show_log:
            logger.info(f'Requested URL: {url} with query payload: {payload}')
        response = requests.post(url, headers=self.headers, data=payload)

        if response.status_code != 200:
            raise ConnectionError(f"Tải dữ liệu không thành công: {response.status_code} - {response.reason}")

        data = response.json()

        # Initialize an empty list to hold all row dictionaries
        rows = []

        # Process each item in the JSON data
        for item in data:
            # Prepare nested dictionaries with higher indices: 'listing', 'bidAsk', 'match'
            item_data = {
                'listing': item['listingInfo'],
                'bidAsk': item['bidAsk'],
                'match': item['matchPrice']
            }

            # Flatten the nested dictionary while preserving the hierarchy in the keys
            row = flatten_data(item_data)

            try:
                # Add bid and ask prices and volumes dynamically with hierarchical keys
                for i, bid in enumerate(item['bidAsk']['bidPrices'], start=1):
                    row[f'bidAsk_bid_{i}_price'] = bid['price']
                    row[f'bidAsk_bid_{i}_volume'] = bid['volume']

                for i, ask in enumerate(item['bidAsk']['askPrices'], start=1):
                    row[f'bidAsk_ask_{i}_price'] = ask['price']
                    row[f'bidAsk_ask_{i}_volume'] = ask['volume']
            except:
                pass
            
            # Append the row dictionary to the list
            rows.append(row)

        # Convert the list of dictionaries to a DataFrame
        combine_df = pd.DataFrame(rows)

        # Transform column names using camel_to_snake and create a MultiIndex
        combine_df.columns = pd.MultiIndex.from_tuples([
            tuple(camel_to_snake(part) for part in c.split('_', 1)) for c in combine_df.columns
        ])

        drop_columns = [('bid_ask', 'code'), ('bid_ask', 'symbol'), ('bid_ask', 'session'), ('bid_ask', 'received_time'), ('bid_ask', 'message_type'), ('bid_ask', 'time'), ('bid_ask', 'bid_prices'), ('bid_ask', 'ask_prices'),
                ('listing', 'code'), ('listing', 'exercise_price'), ('listing', 'exercise_ratio'), ('listing', 'maturity_date'), ('listing', 'underlying_symbol'), ('listing', 'issuer_name'), ('listing', 'received_time'), ('listing', 'message_type'), ('listing', 'en_organ_name'), ('listing', 'en_organ_short_name'), ('listing', 'organ_short_name'), ('listing', 'ticker'),
                ('match', 'code'), ('match', 'symbol'), ('match', 'received_time'), ('match', 'message_type'), ('match', 'time'), ('match', 'session')]
        
        # Drop columns only if they exist in the DataFrame
        combine_df = combine_df.drop(columns=[col for col in drop_columns if col in combine_df.columns])

        # rename column for board inside listing to exchange
        combine_df = combine_df.rename(columns={'board': 'exchange'}, level=1)

        if flatten_columns:
            combine_df = flatten_hierarchical_index(
                combine_df, 
                separator=separator,
                drop_levels=drop_levels,
                handle_duplicates=True
            )

        combine_df.attrs['source'] = 'VCI'

        if to_df:
            return combine_df
        else:
            return data
