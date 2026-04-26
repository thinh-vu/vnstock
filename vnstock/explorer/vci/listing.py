"""Listing module."""

# Đồ thị giá, đồ thị dư mua dư bán, đồ thị mức giá vs khối lượng, thống kê hành vi thị tường
from typing import Optional, List
from datetime import datetime
from .const import _GROUP_CODE, _TRADING_URL, _GRAPHQL_URL
import json
import requests
import pandas as pd
from vnstock.core.utils.parser import camel_to_snake
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers
from vnstock.core.utils.client import send_request, ProxyConfig
from vnstock.core.utils.transform import drop_cols_by_pattern, reorder_cols
from vnstock.common import indices as market_indices
from vnai import optimize_execution
logger = get_logger(__name__)

class Listing:
    """Cấu hình truy cập dữ liệu lịch sử giá chứng khoán từ VCI."""

    def __init__(self, random_agent: Optional[bool] = False, show_log: Optional[bool] = False,
                 proxy_config: Optional[ProxyConfig] = None,
                 proxy_mode: Optional[str] = None,
                 proxy_list: Optional[List[str]] = None):
        self.data_source = 'VCI'
        self.base_url = _TRADING_URL
        self.headers = get_headers(data_source=self.data_source, random_agent=random_agent)
        self.show_log = show_log

        # Handle proxy configuration
        if proxy_config is None:
            # Create ProxyConfig from individual arguments
            p_mode = proxy_mode if proxy_mode else 'try'
            # If user asks for 'auto' or provides list, set request_mode to PROXY
            req_mode = 'direct'
            if proxy_mode == 'auto' or (proxy_list and len(proxy_list) > 0):
                req_mode = 'proxy'
                
            self.proxy_config = ProxyConfig(
                proxy_mode=p_mode,
                proxy_list=proxy_list,
                request_mode=req_mode
            )
        else:
            self.proxy_config = proxy_config

        if not show_log:
            logger.setLevel('CRITICAL')

    @optimize_execution("VCI")
    def all_symbols(self, show_log: Optional[bool] = False) -> pd.DataFrame:
        """Truy xuất danh sách toàn bộ mã và tên các cổ phiếu trên thị trường Việt Nam.

        Args:
            show_log: Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
        """
        df = self.symbols_by_exchange(show_log=show_log)
        df = df.query('type == "STOCK"').reset_index(drop=True)
        df = df[['symbol', 'organ_name']]

        return df
        
    @optimize_execution("VCI")
    def symbols_by_industries(self, lang: str = 'vi', show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Truy xuất thông tin phân ngành icb của các mã cổ phiếu trên thị trường Việt Nam.

        Tham số:
            - lang (tùy chọn): Ngôn ngữ hiển thị. Mặc định là 'vi'.
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
        """
        if lang not in ['vi', 'en']:
            raise ValueError("Tham số lang phải là 'vi' hoặc 'en'.")

        lang_code = '1' if lang == 'vi' else '2'
        url = f"https://iq.vietcap.com.vn/api/iq-insight-service/v2/company/search-bar?language={lang_code}"

        # Use the send_request utility from api_client
        json_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            show_log=show_log,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode
        )

        if not json_data or 'data' not in json_data or json_data['data'] is None:
            raise ValueError("Không nhận được dữ liệu (data) từ VCI. Có thể API đã thay đổi cấu trúc hoặc bị chặn.")

        if show_log:
            logger.info(f'Truy xuất thành công dữ liệu danh sách phân ngành icb.')

        parsed_data = []
        for company in json_data['data']:
            symbol = company.get('code')
            organ_name = company.get('name')
            com_type_code = company.get('comTypeCode')

            for level in range(1, 5):
                icb_key = f'icbLv{level}'
                if icb_key in company and company[icb_key] is not None:
                    parsed_data.append({
                        'symbol': symbol,
                        'organ_name': organ_name,
                        'com_type_code': com_type_code,
                        'icb_level': level,
                        'icb_code': company[icb_key].get('code'),
                        'icb_name': company[icb_key].get('name')
                    })

        df = pd.DataFrame(parsed_data)

        if not df.empty:
            # Filter out empty ICB codes
            df = df[df['icb_code'].notna() & (df['icb_code'] != '')]
            # Sort by symbol and level
            df = df.sort_values(by=['symbol', 'icb_level']).reset_index(drop=True)
            df = df[['symbol', 'organ_name', 'com_type_code', 'icb_level', 'icb_code', 'icb_name']]

        df.source = "VCI"

        return df

    @optimize_execution("VCI")
    def symbols_by_exchange(self, lang: str = 'vi', show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Truy xuất thông tin niêm yết theo sàn của các mã cổ phiếu trên thị trường Việt Nam.

        Tham số:
            - lang (tùy chọn): Ngôn ngữ hiển thị. Mặc định là 'vi'.
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
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
            show_log=show_log,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode
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

        # Set metadata attributes
        df.source = "VCI"
        return df

    @optimize_execution("VCI")
    def industries_icb(self, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Truy xuất thông tin phân ngành icb của các mã cổ phiếu trên thị trường Việt Nam.

        Tham số:
            - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng. Mặc định là False.
        """
        url = "https://iq.vietcap.com.vn/api/iq-insight-service/v1/sectors/icb-codes"

        # Use the send_request utility from api_client
        json_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            show_log=show_log,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode
        )

        if not json_data:
            raise ValueError("Không tìm thấy dữ liệu. Vui lòng kiểm tra lại.")

        if 'data' not in json_data or json_data['data'] is None:
            raise ValueError("Không nhận được dữ liệu (data) từ VCI. Có thể API đã thay đổi cấu trúc hoặc bị chặn.")

        if show_log:
            logger.info('Truy xuất thành công dữ liệu danh sách phân ngành icb.')

        df = pd.DataFrame(json_data['data'])
        df = df.rename(columns={
            'name': 'icb_code',
            'viSector': 'icb_name',
            'enSector': 'en_icb_name',
            'icbLevel': 'level'
        })

        if not df.empty:
            df = df[['icb_name', 'en_icb_name', 'icb_code', 'level']]
            df = df.sort_values(by=['icb_code']).reset_index(drop=True)

        df.source = "VCI"

        return df

    @optimize_execution("VCI")
    def symbols_by_group(self, group: str = 'VN30', show_log: Optional[bool] = False) -> pd.Series:
        """
        Truy xuất danh sách các mã cổ phiếu theo tên nhóm trên thị trường Việt Nam.

        Tham số:
            - group (tùy chọn): Tên nhóm cổ phiếu. Mặc định là 'VN30'.
            - show_log (tùy chọn): Hiển thị thông tin log. Mặc định là False.
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
            show_log=show_log,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode
        )

        if show_log:
            logger.info('Truy xuất thành công dữ liệu danh sách mã theo nhóm.')

        df = pd.DataFrame(json_data)

        if not json_data:
            raise ValueError("JSON data is empty or not provided.")
        # Set metadata attributes
        df.source = "VCI"
        return df['symbol']

    @optimize_execution("VCI")
    def all_future_indices(self, show_log: Optional[bool] = False) -> pd.Series:
        return self.symbols_by_group(group='FU_INDEX', show_log=show_log)

    @optimize_execution("VCI")
    def all_government_bonds(self, show_log: Optional[bool] = False) -> pd.Series:
        return self.symbols_by_group(group='FU_BOND', show_log=show_log)

    @optimize_execution("VCI")
    def all_covered_warrant(self, show_log: Optional[bool] = False) -> pd.Series:
        return self.symbols_by_group(group='CW', show_log=show_log)

    @optimize_execution("VCI")
    def all_bonds(self, show_log: Optional[bool] = False) -> pd.Series:
        return self.symbols_by_group(group='BOND', show_log=show_log)

    # =========================================================================
    # STANDARDIZED MARKET INDICES (Wrapper functions)
    # =========================================================================
    # Provide access to standardized indices across all data sources
    # (VCI, MSN, etc.). Sector indices include mapping to ICB
    # sector_id for industry filtering and analysis.

    def all_indices(self) -> pd.DataFrame:
        """
        Lấy danh sách tất cả các chỉ số tiêu chuẩn hóa với thông tin đầy đủ.

        Returns:
            pd.DataFrame: Columns [symbol, name, description, full_name,
                                   group, index_id, sector_id (for sectors)]
        """
        return market_indices.get_all_indices()

    def indices_by_group(self, group: str) -> Optional[pd.DataFrame]:
        """
        Lấy danh sách chỉ số theo nhóm tiêu chuẩn hóa.

        Args:
            group: Tên nhóm (VD: 'HOSE Indices', 'Sector Indices', etc.)

        Returns:
            pd.DataFrame: Danh sách chỉ số trong nhóm hoặc None
                          (Sector indices include sector_id mapping)
        """
        return market_indices.get_indices_by_group(group)


# Register provider
from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401
ProviderRegistry.register('listing', 'vci', Listing)
