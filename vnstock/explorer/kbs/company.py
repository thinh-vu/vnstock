"""Company module for KB Securities (KBS) data source."""

import json
import pandas as pd
from typing import Dict, Optional, List
import re
from vnai import agg_execution
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.parser import get_asset_type, camel_to_snake
from vnstock.core.utils.transform import clean_html_dict
from vnstock.core.utils.client import send_request, ProxyConfig
from vnstock.core.utils.user_agent import get_headers
from vnstock.explorer.kbs.const import (
    _STOCK_INFO_URL, _IIS_BASE_URL, _SAS_NEWS_URL,
    _PROFILE_MAP, _EVENT_TYPE,
    _COMPANY_PROFILE_MAP, _SUBSIDIARIES_MAP, _LEADERS_MAP,
    _OWNERSHIP_MAP, _SHAREHOLDERS_MAP, _CHARTER_CAPITAL_MAP,
    _LABOR_STRUCTURE_MAP, _EXCHANGE_CODE_MAP
)

logger = get_logger(__name__)


class Company:
    """
    Lớp truy cập thông tin công ty từ KB Securities (KBS).
    
    Tính năng:
    - Fetch dữ liệu công ty từ API (một lần)
    - Cache dữ liệu để tránh gọi lại
    - Xử lý và trả về từng nhóm dữ liệu theo method được gọi
    - Tương tự cấu trúc của VCI Company
    """

    def __init__(
        self,
        symbol: str,
        random_agent: Optional[bool] = False,
        proxy_config: Optional[ProxyConfig] = None,
        show_log: Optional[bool] = False,
        proxy_mode: Optional[str] = None,
        proxy_list: Optional[List[str]] = None,
    ):
        """
        Khởi tạo Company client cho KBS.

        Args:
            symbol: Mã chứng khoán (VD: 'ACB', 'VNM').
            random_agent: Sử dụng user agent ngẫu nhiên. Mặc định False.
            proxy_config: Cấu hình proxy. Mặc định None.
            show_log: Hiển thị log debug. Mặc định False.
            proxy_mode: Chế độ proxy (try, rotate, random, single). Mặc định None.
            proxy_list: Danh sách proxy URLs. Mặc định None.

        Raises:
            ValueError: Nếu mã không phải là cổ phiếu.
        """
        self.symbol = symbol.upper()
        self.asset_type = get_asset_type(self.symbol)

        # Validate if symbol is a stock
        if self.asset_type not in ['stock']:
            raise ValueError("Mã CK không hợp lệ hoặc không phải cổ phiếu.")

        self.data_source = 'KBS'
        self.headers = get_headers(data_source=self.data_source, random_agent=random_agent)
        self.show_log = show_log
        
        # Handle proxy configuration
        if proxy_config is None:
            # Create ProxyConfig from individual arguments
            p_mode = proxy_mode if proxy_mode else 'try'
            # If user provides list, set request_mode to PROXY
            req_mode = 'direct'
            if proxy_list and len(proxy_list) > 0:
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
        
        # Cache for raw data (fetch once, use multiple times)
        self._raw_data = None
        self._cache_loaded = False

    def _load_cache(self, show_log: Optional[bool] = False) -> Dict:
        """
        Fetch và cache dữ liệu công ty từ API (một lần).
        
        Returns:
            Dictionary chứa tất cả dữ liệu công ty.
        """
        if self._cache_loaded and self._raw_data is not None:
            return self._raw_data
        
        url = f'{_STOCK_INFO_URL}/profile/{self.symbol}'
        params = {'l': 1}  # Language param (1 for Vietnamese)

        json_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            params=params,
            show_log=show_log or self.show_log,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode
        )

        self._raw_data = json_data
        self._cache_loaded = True
        return json_data
    
    def _fetch_profile(self, show_log: Optional[bool] = False) -> Dict:
        """
        Lấy thông tin profile công ty từ cache hoặc API.

        Args:
            show_log: Hiển thị log debug.

        Returns:
            Dictionary chứa thông tin profile công ty.
        """
        return self._load_cache(show_log=show_log)

    def _process_profile_data(self, raw_data: Dict) -> pd.DataFrame:
        """
        Xử lý dữ liệu profile thô từ API.
        
        Args:
            raw_data: Dữ liệu thô từ API
            
        Returns:
            DataFrame chứa thông tin profile chuẩn hoá
        """
        if not raw_data:
            return pd.DataFrame()
        
        # Extract profile fields
        profile_dict = {}
        for api_key, schema_key in _COMPANY_PROFILE_MAP.items():
            if api_key in raw_data:
                profile_dict[schema_key] = raw_data[api_key]
        
        # Clean HTML content
        profile_dict = clean_html_dict(profile_dict)
        
        # Extract employee count from labor structure if available
        if 'LaborStructure' in raw_data and raw_data['LaborStructure']:
            labor_data = raw_data['LaborStructure']
            if isinstance(labor_data, list) and len(labor_data) > 0:
                # Sum up all employee counts from labor structure
                total_employees = sum(
                    int(item.get('Value', 0)) 
                    for item in labor_data 
                    if isinstance(item.get('Value'), (int, str))
                )
                if total_employees > 0:
                    profile_dict['number_of_employees'] = total_employees
        
        # Convert to DataFrame
        df = pd.DataFrame([profile_dict])
        
        # Normalize exchange code
        if 'exchange' in df.columns:
            df['exchange'] = df['exchange'].map(
                lambda x: _EXCHANGE_CODE_MAP.get(x, x) if pd.notna(x) else x
            )
        
        # Add metadata
        df.attrs['symbol'] = self.symbol
        df.attrs['source'] = self.data_source
        
        return df
    
    def _process_subsidiaries(self, raw_data: Dict) -> pd.DataFrame:
        """
        Xử lý dữ liệu công ty con từ API.
        
        Args:
            raw_data: Dữ liệu thô từ API
            
        Returns:
            DataFrame chứa thông tin công ty con
        """
        if 'Subsidiaries' not in raw_data or not raw_data['Subsidiaries']:
            return pd.DataFrame()
        
        # Convert list to DataFrame
        df = pd.DataFrame(raw_data['Subsidiaries'])
        
        # Rename columns
        df = df.rename(columns=_SUBSIDIARIES_MAP)
        
        # Convert date columns
        for col in ['date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Add metadata
        df.attrs['symbol'] = self.symbol
        df.attrs['source'] = self.data_source
        
        return df
    
    def _process_leaders(self, raw_data: Dict) -> pd.DataFrame:
        """
        Xử lý dữ liệu ban lãnh đạo từ API.
        
        Args:
            raw_data: Dữ liệu thô từ API
            
        Returns:
            DataFrame chứa thông tin ban lãnh đạo
        """
        if 'Leaders' not in raw_data or not raw_data['Leaders']:
            return pd.DataFrame()
        
        # Convert list to DataFrame
        df = pd.DataFrame(raw_data['Leaders'])
        
        # Rename columns
        df = df.rename(columns=_LEADERS_MAP)
        
        # Add metadata
        df.attrs['symbol'] = self.symbol
        df.attrs['source'] = self.data_source
        
        return df
    
    def _process_ownership(self, raw_data: Dict) -> pd.DataFrame:
        """
        Xử lý dữ liệu cơ cấu cổ đông từ API.
        
        Args:
            raw_data: Dữ liệu thô từ API
            
        Returns:
            DataFrame chứa thông tin cơ cấu cổ đông
        """
        if 'Ownership' not in raw_data or not raw_data['Ownership']:
            return pd.DataFrame()
        
        # Convert list to DataFrame
        df = pd.DataFrame(raw_data['Ownership'])
        
        # Rename columns
        df = df.rename(columns=_OWNERSHIP_MAP)
        
        # Convert date columns
        for col in ['date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Add metadata
        df.attrs['symbol'] = self.symbol
        df.attrs['source'] = self.data_source
        
        return df
    
    def _process_shareholders(self, raw_data: Dict) -> pd.DataFrame:
        """
        Xử lý dữ liệu cổ đông lớn từ API.
        
        Args:
            raw_data: Dữ liệu thô từ API
            
        Returns:
            DataFrame chứa thông tin cổ đông lớn
        """
        if 'Shareholders' not in raw_data or not raw_data['Shareholders']:
            return pd.DataFrame()
        
        # Convert list to DataFrame
        df = pd.DataFrame(raw_data['Shareholders'])
        
        # Rename columns
        df = df.rename(columns=_SHAREHOLDERS_MAP)
        
        # Convert date columns
        for col in ['date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Add metadata
        df.attrs['symbol'] = self.symbol
        df.attrs['source'] = self.data_source
        
        return df
    
    def _process_charter_capital(self, raw_data: Dict) -> pd.DataFrame:
        """
        Xử lý dữ liệu lịch sử vốn điều lệ từ API.
        
        Args:
            raw_data: Dữ liệu thô từ API
            
        Returns:
            DataFrame chứa lịch sử vốn điều lệ
        """
        if 'CharterCapital' not in raw_data or not raw_data['CharterCapital']:
            return pd.DataFrame()
        
        # Convert list to DataFrame
        df = pd.DataFrame(raw_data['CharterCapital'])
        
        # Rename columns
        df = df.rename(columns=_CHARTER_CAPITAL_MAP)
        
        # Convert date columns
        for col in ['date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Add metadata
        df.attrs['symbol'] = self.symbol
        df.attrs['source'] = self.data_source
        
        return df
    
    def _process_labor_structure(self, raw_data: Dict) -> pd.DataFrame:
        """
        Xử lý dữ liệu cơ cấu lao động từ API.
        
        Args:
            raw_data: Dữ liệu thô từ API
            
        Returns:
            DataFrame chứa cơ cấu lao động
        """
        if 'LaborStructure' not in raw_data or not raw_data['LaborStructure']:
            return pd.DataFrame()
        
        # Convert list to DataFrame
        df = pd.DataFrame(raw_data['LaborStructure'])
        
        # Rename columns
        df = df.rename(columns=_LABOR_STRUCTURE_MAP)
        
        # Add metadata
        df.attrs['symbol'] = self.symbol
        df.attrs['source'] = self.data_source
        
        return df

    @agg_execution("KBS")
    def overview(self, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Truy xuất thông tin tổng quan của công ty.

        Args:
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa thông tin tổng quan công ty.

        Examples:
            >>> company = Company('ACB')
            >>> df = company.overview()
            >>> print(df.columns.tolist()[:5])
            ['business_model', 'symbol', 'founded_date', 'charter_capital', 'num_employees']
        """
        profile_data = self._fetch_profile(show_log=show_log)

        if not profile_data:
            raise ValueError(f"Không tìm thấy dữ liệu profile cho mã {self.symbol}.")

        # Process profile data with caching
        df = self._process_profile_data(profile_data)

        if show_log or self.show_log:
            logger.info(f'Truy xuất thành công thông tin tổng quan cho {self.symbol}.')

        return df

    @agg_execution("KBS")
    def officers(self, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Truy xuất thông tin lãnh đạo công ty (officers).

        Args:
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa thông tin lãnh đạo.

        Examples:
            >>> company = Company('ACB')
            >>> df = company.officers()
            >>> print(df.columns.tolist())
            ['from_date', 'position_name_vn', 'name', 'position_en', 'position_id']
        """
        profile_data = self._fetch_profile(show_log=show_log)

        if not profile_data:
            return pd.DataFrame()

        df = self._process_leaders(profile_data)

        if show_log or self.show_log:
            logger.info(f'Truy xuất thành công {len(df)} lãnh đạo công ty cho {self.symbol}.')

        return df
    
    @agg_execution("KBS")
    def shareholders(self, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Truy xuất thông tin cổ đông của công ty.

        Args:
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa thông tin cổ đông.

        Examples:
            >>> company = Company('ACB')
            >>> df = company.shareholders()
            >>> print(df.columns.tolist())
            ['name', 'date', 'shares', 'ownership_ratio']
        """
        profile_data = self._fetch_profile(show_log=show_log)

        if not profile_data:
            return pd.DataFrame()

        df = self._process_shareholders(profile_data)

        if show_log or self.show_log:
            logger.info(f'Truy xuất thành công {len(df)} cổ đông cho {self.symbol}.')

        return df
    
    @agg_execution("KBS")
    def ownership(self, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Truy xuất cơ cấu cổ đông của công ty.

        Args:
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa cơ cấu cổ đông.

        Examples:
            >>> company = Company('ACB')
            >>> df = company.ownership()
            >>> print(df.columns.tolist())
            ['owner_type', 'ownership_ratio', 'shares', 'date']
        """
        profile_data = self._fetch_profile(show_log=show_log)

        if not profile_data:
            return pd.DataFrame()

        df = self._process_ownership(profile_data)

        if show_log or self.show_log:
            logger.info(f'Truy xuất thành công cơ cấu cổ đông cho {self.symbol}.')

        return df
    
    @agg_execution("KBS")
    def subsidiaries(self, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Truy xuất thông tin công ty con và công ty liên kết của công ty.
        
        Bao gồm cả công ty con (ownership > 50%) và công ty liên kết (ownership ≤ 50%),
        với cột 'type' để phân biệt.

        Args:
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa thông tin công ty con và công ty liên kết.

        Examples:
            >>> company = Company('ACB')
            >>> df = company.subsidiaries()
            >>> print(df.columns.tolist())
            ['date', 'name', 'charter_capital', 'ownership_ratio', 'currency', 'type']
        """
        profile_data = self._fetch_profile(show_log=show_log)

        if not profile_data:
            return pd.DataFrame()

        df = self._process_subsidiaries(profile_data)
        
        if len(df) > 0:
            # Add type column to distinguish subsidiaries and affiliates
            df['type'] = df['ownership_percent'].apply(
                lambda x: 'công ty con' if x > 50 else 'công ty liên kết'
            )

        if show_log or self.show_log:
            logger.info(f'Truy xuất thành công {len(df)} công ty con/liên kết cho {self.symbol}.')

        return df
    
    @agg_execution("KBS")
    def affiliate(self, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Truy xuất thông tin công ty liên kết của công ty (ownership ≤ 50%).
        
        Công ty liên kết được định nghĩa là các công ty có tỷ lệ sở hữu tối đa 50%.
        Dữ liệu được lọc từ danh sách công ty con.

        Args:
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa thông tin công ty liên kết.
        """
        profile_data = self._fetch_profile(show_log=show_log)

        if not profile_data:
            return pd.DataFrame()

        df = self._process_subsidiaries(profile_data)
        
        if len(df) == 0:
            return df
        
        # Filter affiliates: ownership_percent <= 50%
        df_affiliate = df[df['ownership_percent'] <= 50].copy()
        df_affiliate['type'] = 'công ty liên kết'
        
        if show_log or self.show_log:
            logger.info(f'Truy xuất thành công {len(df_affiliate)} công ty liên kết cho {self.symbol}.')
        
        return df_affiliate
    
    @agg_execution("KBS")
    def capital_history(self, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Truy xuất lịch sử vốn điều lệ của công ty.

        Args:
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa lịch sử vốn điều lệ.

        Examples:
            >>> company = Company('ACB')
            >>> df = company.capital_history()
            >>> print(df.columns.tolist())
            ['date', 'value', 'currency']
        """
        profile_data = self._fetch_profile(show_log=show_log)

        if not profile_data:
            return pd.DataFrame()

        df = self._process_charter_capital(profile_data)

        if show_log or self.show_log:
            logger.info(f'Truy xuất thành công lịch sử vốn điều lệ cho {self.symbol}.')

        return df
    
    @agg_execution("KBS")
    def events(
        self,
        event_type: Optional[int] = None,
        page: int = 1,
        page_size: int = 10,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Truy xuất danh sách sự kiện của công ty.

        Args:
            event_type: Loại sự kiện (1-5). None để lấy tất cả. 
                        1: Đại hội cổ đông, 2: Trả cổ tức, 3: Phát hành,
                        4: Giao dịch cổ đông nội bộ, 5: Sự kiện khác.
            page: Số trang. Mặc định 1.
            page_size: Số lượng bản ghi mỗi trang. Mặc định 10.
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa danh sách sự kiện.

        Examples:
            >>> company = Company('ACB')
            >>> df = company.events(event_type=2)  # Sự kiện trả cổ tức
        """
        url = f'{_STOCK_INFO_URL}/event/{self.symbol}'
        
        # Build params
        params = {
            'l': 1,  # Language
            'p': page,
            's': page_size,
        }

        if event_type is not None:
            if event_type not in _EVENT_TYPE:
                raise ValueError(
                    f"event_type không hợp lệ. Các giá trị hợp lệ: {list(_EVENT_TYPE.keys())}"
                )
            params['eID'] = event_type

        json_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            params=params,
            show_log=show_log or self.show_log,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode
        )

        if not json_data:
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(json_data)

        # Convert column names to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]

        # Add metadata
        df.attrs['symbol'] = self.symbol
        df.attrs['source'] = self.data_source
        if event_type:
            df.attrs['event_type'] = _EVENT_TYPE[event_type]

        if show_log or self.show_log:
            logger.info(f'Truy xuất thành công {len(df)} sự kiện cho {self.symbol}.')

        return df

    @agg_execution("KBS")
    def news(
        self,
        page: int = 1,
        page_size: int = 10,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Truy xuất tin tức liên quan đến công ty.

        Args:
            page: Số trang. Mặc định 1.
            page_size: Số lượng bản ghi mỗi trang. Mặc định 10.
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa danh sách tin tức.

        Examples:
            >>> company = Company('ACB')
            >>> df = company.news(page=1, page_size=20)
        """
        url = f'{_STOCK_INFO_URL}/news/{self.symbol}'
        
        params = {
            'l': 1,  # Language
            'p': page,
            's': page_size,
        }

        json_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            params=params,
            show_log=show_log or self.show_log,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode
        )

        if not json_data:
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(json_data)

        # Convert column names to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]

        # Add metadata
        df.attrs['symbol'] = self.symbol
        df.attrs['source'] = self.data_source

        if show_log or self.show_log:
            logger.info(f'Truy xuất thành công {len(df)} tin tức cho {self.symbol}.')

        return df

    @agg_execution("KBS")
    def insider_trading(
        self,
        page: int = 1,
        page_size: int = 10,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Truy xuất thông tin giao dịch nội bộ.

        Args:
            page: Số trang. Mặc định 1.
            page_size: Số lượng bản ghi mỗi trang. Mặc định 10.
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa thông tin giao dịch nội bộ.

        Examples:
            >>> company = Company('ACB')
            >>> df = company.insider_trading()
        """
        url = f'{_STOCK_INFO_URL}/news/internal-trading/{self.symbol}'
        
        params = {
            'l': 1,  # Language
            'p': page,
            's': page_size,
        }

        json_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            params=params,
            show_log=show_log or self.show_log,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode
        )

        if not json_data:
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(json_data)

        # Convert column names to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]

        # Add metadata
        df.attrs['symbol'] = self.symbol
        df.attrs['source'] = self.data_source

        if show_log or self.show_log:
            logger.info(
                f'Truy xuất thành công {len(df)} bản ghi giao dịch nội bộ cho {self.symbol}.'
            )

        return df


# Register KBS Company provider
from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401
ProviderRegistry.register('company', 'kbs', Company)
