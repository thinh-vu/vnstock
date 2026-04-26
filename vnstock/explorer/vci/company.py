"""
Module quản lý thông tin công ty từ nguồn dữ liệu VCI.
"""

import json
import pandas as pd
from typing import Dict, Optional, Union, List
from datetime import datetime, timedelta
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.transform import clean_html_dict, flatten_dict_to_df, flatten_list_to_df, reorder_cols, drop_cols_by_pattern
from vnstock.core.utils.client import send_request
from vnstock.core.utils.user_agent import get_headers
from vnstock.core.utils.parser import get_asset_type, camel_to_snake
from vnai import optimize_execution  # Import the decorator from vnai package
from vnstock.explorer.vci.const import _VCIQ_URL, _VCI_COMPANY_URL

logger = get_logger(__name__)

class Company:
    """
    Class (lớp) quản lý các thông tin liên quan đến công ty từ nguồn dữ liệu VCI.

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
            
        self.headers = get_headers(data_source='VCI', random_agent=random_agent)
        self.show_log = show_log
        self.to_df = to_df
        self.base_url = _VCI_COMPANY_URL
        
        if not show_log:
            logger.setLevel('CRITICAL')

    def _fetch_company_details(self) -> Dict:
        """
        Fetch company overview details from REST API.
        
        Returns:
            Dict: Company details data.
        """
        url = f"{self.base_url}/details?ticker={self.symbol}"

        if self.show_log:
            logger.debug(f"Requesting company details for {self.symbol} from {url}")

        response_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            show_log=self.show_log
        )
        
        return response_data.get('data', {})

    def _fetch_shareholders(self) -> Dict:
        """
        Fetch shareholder structure from REST API.

        Returns:
            Dict: Shareholder data.
        """
        url = f"{self.base_url}/{self.symbol}/shareholder-structure"
        
        if self.show_log:
            logger.debug(f"Requesting shareholder structure for {self.symbol} from {url}")

        response_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            show_log=self.show_log
        )
        
        return response_data.get('data', {})

    def _fetch_shareholder_list(self) -> Dict:
        """
        Fetch shareholder list from REST API (includes both individuals and organizations).

        Returns:
            Dict: Shareholder list data.
        """
        url = f"{self.base_url}/{self.symbol}/shareholder"

        if self.show_log:
            logger.debug(f"Requesting shareholder list for {self.symbol} from {url}")

        response_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            show_log=self.show_log
        )

        return response_data.get('data', [])

    def _fetch_relationships(self) -> Dict:
        """
        Fetch subsidiary and affiliate relationships from REST API.

        Returns:
            Dict: Relationship data.
        """
        url = f"{self.base_url}/{self.symbol}/relationship"

        if self.show_log:
            logger.debug(f"Requesting relationships for {self.symbol} from {url}")

        response_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            show_log=self.show_log
        )

        return response_data.get('data', {})
    
    def _fetch_news_events(self, from_date: str = None, to_date: str = None,
                          event_codes: str = None) -> List:
        """
        Fetch news and events from REST API.
        
        Returns:
            List: News and events data.
        """
        if from_date is None:
            from_date = (datetime.now() - timedelta(days=120)).strftime('%Y%m%d')
        if to_date is None:
            to_date = datetime.now().strftime('%Y%m%d')
        if event_codes is None:
            event_codes = 'DIV,ISS'
        
        url = f"{_VCIQ_URL}/v1/news-events-for-chart?ticker={self.symbol}&fromDate={from_date}&toDate={to_date}&languageId=1&eventCode={event_codes}"
        
        if self.show_log:
            logger.debug(f"Requesting news and events for {self.symbol} from {url}")

        response_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            show_log=self.show_log
        )

        return response_data.get('data', [])
    
    def _fetch_news(self, from_date: str = None, to_date: str = None,
                   page: int = 0, size: int = 50) -> List:
        """
        Fetch news from REST API (alternative endpoint with more data).

        Returns:
            List: News data.
        """
        if from_date is None:
            from_date = (datetime.now() - timedelta(days=365*10)).strftime('%Y%m%d')
        if to_date is None:
            to_date = datetime.now().strftime('%Y%m%d')

        url = f"{_VCIQ_URL}/v1/news?ticker={self.symbol}&fromDate={from_date}&toDate={to_date}&languageId=1&page={page}&size={size}"

        if self.show_log:
            logger.debug(f"Requesting news for {self.symbol} from {url}")

        response_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            show_log=self.show_log
        )

        # Extract content from paginated response
        data = response_data.get('data', {})
        if isinstance(data, dict):
            return data.get('content', [])
        return []

    def _fetch_financial_statistics(self) -> Dict:
        """
        Fetch financial statistics summary from REST API.

        Returns:
            Dict: Financial statistics data.
        """
        url = f"{self.base_url}/{self.symbol}/statistics-financial"

        if self.show_log:
            logger.debug(f"Requesting financial statistics for {self.symbol} from {url}")

        response_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            show_log=self.show_log
        )

        return response_data.get('data', {})


    @optimize_execution("VCI")
    def _info(self) -> pd.DataFrame:
        """
        Truy xuất thông tin công ty theo chuẩn schema mapping.

        Returns:
            pd.DataFrame: DataFrame chứa thông tin công ty với columns chuẩn hóa.
        """
        data = self._fetch_company_details()

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame([data])

        # Map columns theo SCHEMA_MAP (camelCase from API)
        # Priority: use Vietnamese names first, then English
        result = {}

        # Symbol
        if 'ticker' in df.columns:
            result['symbol'] = df['ticker'].iloc[0]

        # Name (prefer Vietnamese)
        if 'viOrganName' in df.columns:
            result['name'] = df['viOrganName'].iloc[0]
        elif 'enOrganName' in df.columns:
            result['name'] = df['enOrganName'].iloc[0]

        # Short name (prefer Vietnamese)
        if 'viOrganShortName' in df.columns:
            result['short_name'] = df['viOrganShortName'].iloc[0]
        elif 'enOrganShortName' in df.columns:
            result['short_name'] = df['enOrganShortName'].iloc[0]

        # Sector (prefer Vietnamese)
        if 'sectorVn' in df.columns:
            result['sector'] = df['sectorVn'].iloc[0]
        elif 'sector' in df.columns:
            result['sector'] = df['sector'].iloc[0]

        # Profile (prefer Vietnamese)
        if 'profile' in df.columns:
            result['profile'] = df['profile'].iloc[0]
        elif 'enProfile' in df.columns:
            result['profile'] = df['enProfile'].iloc[0]

        # Listing date
        if 'listingDate' in df.columns:
            result['listing_date'] = df['listingDate'].iloc[0]

        # Convert to DataFrame
        result_df = pd.DataFrame([result])

        # Select only columns that exist
        standard_columns = [
            "symbol", "name", "short_name", "sector", "profile", "listing_date"
        ]

        existing_cols = [col for col in standard_columns if col in result_df.columns]
        result_df = result_df[existing_cols]

        return result_df

    @optimize_execution("VCI")
    def overview(self) -> pd.DataFrame:
        """
        Truy xuất thông tin tổng quan của công ty (raw data từ API).
        
        Returns:
            pd.DataFrame: DataFrame chứa thông tin tổng quan của công ty.
        """
        data = self._fetch_company_details()
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame([data])

        # Convert camelCase to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]
        
        # Drop English columns and internal fields
        df = drop_cols_by_pattern(df, ['en_', '__'])

        # Drop sector_vn if sector already exists (to avoid duplicates)
        if 'sector_vn' in df.columns and 'sector' in df.columns:
            df = df.drop(columns=['sector_vn'])

        # Rename to match old schema names
        rename_map = {
            'vi_organ_name': 'organ_name',
            'vi_organ_short_name': 'organ_short_name',
            'profile': 'company_profile',
            'number_of_shares_mkt_cap': 'issue_share',
            'ticker': 'symbol'
        }
        rename_dict = {k: v for k, v in rename_map.items() if k in df.columns}
        if rename_dict:
            df = df.rename(columns=rename_dict)

        # Clean HTML/CSS from company_profile field
        if 'company_profile' in df.columns:
            import re
            def strip_html(text):
                if not isinstance(text, str):
                    return text
                # Remove HTML tags
                text = re.sub(r'<[^>]+>', '', text)
                # Decode HTML entities
                import html
                text = html.unescape(text)
                # Remove extra whitespace
                text = ' '.join(text.split())
                return text

            df['company_profile'] = df['company_profile'].apply(strip_html)
        
        # Reorder columns with ticker first
        df = reorder_cols(df, ['symbol'], position='first')
        
        return df

    @optimize_execution("VCI")
    def shareholders(self, mode: str = 'detailed') -> pd.DataFrame:
        """
        Truy xuất thông tin cổ đông của công ty.
        
        Tham số:
            - mode (str): Chế độ hiển thị
                - 'summary': Tóm tắt cơ cấu cổ đông (mặc định)
                - 'detailed': Danh sách chi tiết tất cả cổ đông

        Returns:
            pd.DataFrame: DataFrame chứa thông tin cổ đông của công ty.
        """
        if mode == 'summary':
            # Return summary structure
            data = self._fetch_shareholders()

            if not data:
                return pd.DataFrame()

            df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])

            # Convert to snake_case
            df.columns = [camel_to_snake(col) for col in df.columns]

            # Drop unnecessary columns
            df = drop_cols_by_pattern(df, ['__typename', 'ticker', 'en_'])

            # Convert update_date from timestamp to date string if needed
            if 'update_date' in df.columns and df['update_date'].dtype in [int, float]:
                df['update_date'] = pd.to_datetime(df['update_date'], unit='ms').dt.strftime('%Y-%m-%d')

            # Rename columns for clarity
            rename_map = {}
            if 'owner_full_name' in df.columns:
                rename_map['owner_full_name'] = 'share_holder'
            if 'percentage' in df.columns:
                rename_map['percentage'] = 'share_own_percent'
            if rename_map:
                df = df.rename(columns=rename_map)

            return df
        
        elif mode == 'detailed':
            # Return detailed shareholder list
            data = self._fetch_shareholder_list()

            if not data:
                return pd.DataFrame()

            df = pd.DataFrame(data)

            # Convert to snake_case
            df.columns = [camel_to_snake(col) for col in df.columns]

            # Drop unnecessary columns
            df = drop_cols_by_pattern(df, ['__typename', 'ticker', 'en_', 'owner_type', 'owner_code', 'position_name', 'public_date'])

            # Rename to match old schema names
            rename_map = {
                'owner_name': 'share_holder',
                'percentage': 'share_own_percent'
            }
            rename_dict = {k: v for k, v in rename_map.items() if k in df.columns}
            if rename_dict:
                df = df.rename(columns=rename_dict)

            # Add symbol column
            df.insert(0, 'symbol', self.symbol)

            # Select only standard columns (using schema mapping keys)
            standard_columns = ['symbol', 'share_holder', 'quantity', 'share_own_percent', 'update_date']
            existing_cols = [col for col in standard_columns if col in df.columns]
            df = df[existing_cols]

            return df
        
        else:
            raise ValueError(f"Invalid mode: {mode}. Use 'summary' or 'detailed'")
    
    @optimize_execution("VCI")
    def officers(self, filter_by: str = 'working') -> pd.DataFrame:
        """
        Truy xuất thông tin lãnh đạo công ty (cá nhân có vị trí).

        Tham số:
            - filter_by (str): Lọc lãnh đạo đang làm việc hoặc đã từ nhiệm hoặc tất cả.
                - 'working': Lọc lãnh đạo đang làm việc (mặc định).
                - 'resigned': Lọc lãnh đạo đã từ nhiệm.
                - 'all': Lọc tất cả lãnh đạo.

        Returns:
            pd.DataFrame: DataFrame chứa thông tin lãnh đạo của công ty.
        """
        if filter_by not in ['working', 'resigned', 'all']:
            raise ValueError("filter_by chỉ nhận giá trị 'working' hoặc 'resigned' hoặc 'all'")
        
        data = self._fetch_shareholder_list()

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])

        # Convert to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]

        # Filter: only INDIVIDUAL with positionName (lãnh đạo)
        if 'owner_type' in df.columns:
            df = df[df['owner_type'] == 'INDIVIDUAL']

        # Filter: must have a position name (not null)
        if 'position_name' in df.columns:
            df = df[df['position_name'].notna()]
        
        # Drop unnecessary columns
        df = drop_cols_by_pattern(df, ['en_', '__', 'owner_code', 'owner_type', 'public_date'])

        # Rename to match old schema names
        rename_map = {
            'owner_name': 'officer_name',
            'position_name': 'officer_position',
            'percentage': 'officer_own_percent',
            'quantity': 'officer_own_quantity'
        }
        rename_dict = {k: v for k, v in rename_map.items() if k in df.columns}
        if rename_dict:
            df = df.rename(columns=rename_dict)

        # Add symbol column
        df.insert(0, 'symbol', self.symbol)
        
        # Convert date from timestamp to date string if needed
        if 'update_date' in df.columns and df['update_date'].dtype in [int, float]:
            df['update_date'] = pd.to_datetime(df['update_date'], unit='ms').dt.strftime('%Y-%m-%d')
        
        # Select only standard columns (using schema mapping keys)
        standard_columns = ['symbol', 'officer_name', 'officer_position', 'officer_own_percent', 'officer_own_quantity', 'update_date']
        existing_cols = [col for col in standard_columns if col in df.columns]
        df = df[existing_cols]
        
        return df
    
    @optimize_execution("VCI")
    def subsidiaries(self, filter_by: str = 'all') -> pd.DataFrame:
        """
        Truy xuất thông tin công ty con của công ty.

        Tham số:
            - filter_by (str): Lọc công ty con hoặc công ty liên kết.
                - 'all': Lọc tất cả.
                - 'subsidiary': Lọc công ty con.
                - 'affiliate': Lọc công ty liên kết.

        Returns:
            pd.DataFrame: DataFrame chứa thông tin công ty con.
        """
        if filter_by not in ['all', 'subsidiary', 'affiliate']:
            raise ValueError("filter_by chỉ nhận giá trị 'all' hoặc 'subsidiary' hoặc 'affiliate'")
        
        data = self._fetch_relationships()
        
        if not data:
            return pd.DataFrame()
        
        # Handle both dict and list responses
        if isinstance(data, dict):
            subsidiary_list = data.get('subsidiaries', [])
            affiliate_list = data.get('affiliates', [])
        else:
            subsidiary_list = []
            affiliate_list = []
        
        dfs = []

        if filter_by in ['all', 'subsidiary'] and subsidiary_list:
            sub_df = pd.DataFrame(subsidiary_list)
            sub_df.columns = [camel_to_snake(col) for col in sub_df.columns]
            sub_df = drop_cols_by_pattern(sub_df, ['__typename', 'en_'])

            # Rename columns to match old schema names
            rename_map = {
                'right_organ_name_vi': 'organ_name',
                'right_organ_code': 'sub_organ_code',
                'owned_percentage': 'ownership_percent'
            }

            rename_dict = {k: v for k, v in rename_map.items() if k in sub_df.columns}
            if rename_dict:
                sub_df = sub_df.rename(columns=rename_dict)

            # Drop organ_code if exists
            if 'organ_code' in sub_df.columns:
                sub_df = sub_df.drop(columns=['organ_code'])

            sub_df.insert(0, 'symbol', self.symbol)
            dfs.append(sub_df)

        if filter_by in ['all', 'affiliate'] and affiliate_list:
            aff_df = pd.DataFrame(affiliate_list)
            aff_df.columns = [camel_to_snake(col) for col in aff_df.columns]
            aff_df = drop_cols_by_pattern(aff_df, ['__typename', 'en_'])

            # Rename columns to match old schema names
            rename_map = {
                'right_organ_name_vi': 'organ_name',
                'right_organ_code': 'sub_organ_code',
                'owned_percentage': 'ownership_percent'
            }

            rename_dict = {k: v for k, v in rename_map.items() if k in aff_df.columns}
            if rename_dict:
                aff_df = aff_df.rename(columns=rename_dict)

            # Drop organ_code if exists
            if 'organ_code' in aff_df.columns:
                aff_df = aff_df.drop(columns=['organ_code'])

            aff_df.insert(0, 'symbol', self.symbol)
            dfs.append(aff_df)

        if dfs:
            result = pd.concat(dfs, ignore_index=True)

            # Select only standard columns (using old schema names)
            standard_columns = ['symbol', 'organ_name', 'ownership_percent', 'sub_organ_code', 'type']
            existing_cols = [col for col in standard_columns if col in result.columns]
            result = result[existing_cols]

            return result
        else:
            return pd.DataFrame()
        
    @optimize_execution("VCI")
    def affiliate(self) -> pd.DataFrame:
        """
        Truy xuất thông tin công ty liên kết của công ty.
        
        Returns:
            pd.DataFrame: DataFrame chứa thông tin công ty liên kết.
        """
        data = self._fetch_relationships()

        if not data:
            return pd.DataFrame()

        # Extract affiliates from relationship data
        if isinstance(data, dict):
            affiliate_list = data.get('affiliates', [])
        else:
            affiliate_list = []

        if not affiliate_list:
            return pd.DataFrame()

        df = pd.DataFrame(affiliate_list)
        
        # Convert column names to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]
        
        # Drop unnecessary columns
        df = drop_cols_by_pattern(df, ['en_', '__typename'])
        if 'organ_code' in df.columns:
            df = df.drop(columns=['organ_code'])
        
        # Rename percentage to ownership_percent for clarity
        if 'percentage' in df.columns:
            df = df.rename(columns={'percentage': 'ownership_percent'})
        
        return df
      
    @optimize_execution("VCI")
    def news(self) -> pd.DataFrame:
        """
        Truy xuất tin tức liên quan đến công ty.
        
        Returns:
            pd.DataFrame: DataFrame chứa tin tức liên quan đến công ty.
        """
        # Try to fetch from the main news endpoint first (has more data)
        data = self._fetch_news()
        
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        # Convert to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]
        
        # Drop unnecessary columns
        cols_to_drop = [col for col in ['organ_code', 'symbol', '__typename', 'is_event', 'event', 'create_by', 'update_by', 'status', 'create_date', 'update_date', 'source_code', 'expert_id', 'is_tranfer'] if col in df.columns]
        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)
        
        return df
    
    def _fetch_events(self, event_codes: str = None, from_date: str = None,
                     to_date: str = None, page: int = 0, size: int = 50) -> List:
        """
        Fetch events from REST API.

        Args:
            event_codes (str): Event codes to fetch (comma-separated)
                - 'DIV,ISS': Trả cổ tức & phát hành thêm
                - 'DDIND,DDINS,DDRP': Giao dịch cổ đông lớn & cổ đông nội bộ
                - 'AGME,AGMR,EGME': Đại hội cổ đông
                - 'AIS,MA,MOVE,NLIS,OTHE,RETU,SUSP': Sự kiện khác
            from_date (str): Start date in YYYYMMDD format
            to_date (str): End date in YYYYMMDD format
            page (int): Page number (0-indexed)
            size (int): Number of items per page

        Returns:
            List: Events data.
        """
        if event_codes is None:
            # Default: all event types
            event_codes = 'DIV,ISS,DDIND,DDINS,DDRP,AGME,AGMR,EGME,AIS,MA,MOVE,NLIS,OTHE,RETU,SUSP'

        if from_date is None:
            from_date = (datetime.now() - timedelta(days=365*10)).strftime('%Y%m%d')
        if to_date is None:
            to_date = datetime.now().strftime('%Y%m%d')

        url = f"{_VCIQ_URL}/v1/events?ticker={self.symbol}&fromDate={from_date}&toDate={to_date}&eventCode={event_codes}&page={page}&size={size}"

        if self.show_log:
            logger.debug(f"Requesting events for {self.symbol} from {url}")

        response_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            show_log=self.show_log
        )

        # Extract content from paginated response
        data = response_data.get('data', {})
        if isinstance(data, dict):
            return data.get('content', [])
        return []

    @optimize_execution("VCI")
    def events(self) -> pd.DataFrame:
        """
        Truy xuất các sự kiện của công ty.
        
        Returns:
            pd.DataFrame: DataFrame chứa các sự kiện của công ty.
        """
        data = self._fetch_events()
        
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        # Convert to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]
        
        # Drop unnecessary columns
        cols_to_drop = [col for col in ['organ_code', 'symbol', '__typename', 'is_event', 'event', 'organ_name_en', 'organ_name_vi'] if col in df.columns]
        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)
        
        # Convert date columns from timestamp to date string
        date_columns = ['public_date', 'issue_date', 'record_date', 'exright_date', 'display_date']
        for col in date_columns:
            if col in df.columns:
                if df[col].dtype in [int, float]:
                    df[col] = pd.to_datetime(df[col], unit='ms').dt.strftime('%Y-%m-%d')
                elif df[col].dtype == 'object':
                    # Try to parse ISO format dates
                    try:
                        df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
                    except:
                        pass
        
        return df
    


    @optimize_execution("VCI")
    def trading_stats(self) -> pd.DataFrame:
        """
        Truy xuất thống kê giao dịch của công ty.
        
        Returns:
            pd.DataFrame: DataFrame chứa thống kê giao dịch của công ty.
        """
        data = self._fetch_company_details()

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame([data])
        
        # Convert column names to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]
        
        # Drop __typename column
        df = drop_cols_by_pattern(df, ['__typename'])
        
        # Add symbol column
        df['symbol'] = self.symbol
        
        # Reorder to have symbol first
        df = reorder_cols(df, ['symbol'], position='first')
        
        return df
    
    @optimize_execution("VCI")
    def ratio_summary(self) -> pd.DataFrame:
        """
        Truy xuất tóm tắt các tỷ lệ tài chính của công ty.
        
        Returns:
            pd.DataFrame: DataFrame chứa tóm tắt các tỷ lệ tài chính của công ty.
        """
        data = self._fetch_financial_statistics()
        
        if not data:
            return pd.DataFrame()

        # Handle both list and dict responses
        if isinstance(data, list):
            if len(data) == 0:
                return pd.DataFrame()
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data])

        # Convert column names to snake_case (only string column names)
        df.columns = [camel_to_snake(str(col)) for col in df.columns]
        
        # Drop __typename column
        df = drop_cols_by_pattern(df, ['__typename'])
        
        # Add symbol column
        df['symbol'] = self.symbol
        
        # Reorder to have symbol first
        df = reorder_cols(df, cols=['symbol'], position='first')
        
        return df

# Register provider
from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401
ProviderRegistry.register('company', 'vci', Company)
