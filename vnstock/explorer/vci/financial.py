"""
Module quản lý thông tin báo cáo tài chính từ nguồn dữ liệu VCI.
"""

import json
import pandas as pd
from packaging import version

def _safe_infer_objects(df):
    """
    Tự động gọi infer_objects phù hợp với version pandas.
    pandas >= 2.1.0: dùng copy=False
    pandas < 2.1.0: không truyền copy
    """
    if version.parse(pd.__version__) >= version.parse("2.1.0"):
        return df.infer_objects(copy=False)
    else:
        return df.infer_objects()

import pandas as pd
from typing import Optional, List, Dict, Tuple, Union
from .const import _GRAPHQL_URL, _FINANCIAL_REPORT_PERIOD_MAP, _UNIT_MAP, _ICB4_COMTYPE_CODE_MAP, SUPPORTED_LANGUAGES, _VCIQ_URL, _IQ_FINANCE_REPORT
from vnstock.explorer.vci import Company
from vnstock.core.utils import client
from vnstock.core.utils.client import ProxyConfig
from vnstock.core.utils.parser import get_asset_type, camel_to_snake
from vnstock.core.utils.validation import validate_symbol
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers
from vnstock.core.utils.transform import replace_in_column_names, flatten_hierarchical_index, reorder_cols
import requests
import secrets

logger = get_logger(__name__)

class Finance:
    """
    Truy xuất thông tin báo cáo tài chính của một công ty theo mã chứng khoán từ nguồn dữ liệu VCI.

    Tham số:
        - symbol (str): Mã chứng khoán của công ty cần truy xuất thông tin.
        - period (str): Chu kỳ báo cáo tài chính cần truy xuất. Mặc định là 'quarter'.
        - get_all (bool): Trả về tất cả các trường dữ liệu hoặc chỉ các trường chọn lọc. Mặc định là True.
        - show_log (bool): Hiển thị thông tin log hoặc không. Mặc định là True.
    """

    def __init__(self, symbol: str, period: Optional[str] = 'quarter', 
                 get_all: Optional[bool] = True, show_log: Optional[bool] = True,
                 proxy_config: Optional[ProxyConfig] = None,
                 proxy_mode: Optional[str] = None,
                 proxy_list: Optional[List[str]] = None):
        """
        Khởi tạo đối tượng Finance với các tham số cho việc truy xuất dữ liệu báo cáo tài chính.
        """
        self.symbol = validate_symbol(symbol)
        self.asset_type = get_asset_type(self.symbol)
        self.headers = get_headers(data_source='VCI')
        self.show_log = show_log
        self.base_url = _VCIQ_URL
        self._handshake()

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

        # Validate input for period
        if period not in ['year', 'quarter']:
            raise ValueError("Kỳ báo cáo tài chính không hợp lệ. Chỉ chấp nhận 'year' hoặc 'quarter'.")
        
        # If asset_type is not stock, raise error
        if self.asset_type not in ['stock']:
            raise ValueError("Mã chứng khoán không hợp lệ. Chỉ cổ phiếu mới có thông tin.")
            
        self.period = _FINANCIAL_REPORT_PERIOD_MAP.get(period)
        self.get_all = get_all
        self.com_type_code = self._get_company_type()
    
    def _get_company_type(self) -> str:
        """
        Lấy mã loại công ty từ ICB4_COMTYPE_CODE_MAP dựa trên phân loại ngành ICB4 của công ty để ánh xạ báo cáo.

        Returns:
            str: Mã loại công ty. Các giá trị có thể là:
                'CT': Công ty (Company)
                'CK': Chứng khoán (Securities)
                'NH': Ngân hàng (Bank)
                'BH': Bảo hiểm (Insurance)
        """
        # Call the Listing module instead of Company._fetch_data (which relies on a deprecated API structure)
        from vnstock.explorer.vci.listing import Listing
        df_listing = Listing(random_agent=False, show_log=False).symbols_by_industries()
        if not df_listing.empty:
            df_match = df_listing[(df_listing['symbol'] == self.symbol) & (df_listing['icb_level'] == 4)]
            if not df_match.empty:
                return df_match['com_type_code'].iloc[0]

        # Fallback value if not found
        return 'CT'

    @staticmethod
    def duplicated_columns_handling(df_or_mapping, target_col_name=None):
        """
        Handle duplicated column names in a DataFrame or column mapping DataFrame.
        
        Parameters:
            - df_or_mapping (pd.DataFrame): Either a DataFrame with potentially duplicated columns
            or a mapping DataFrame with columns that may have duplicated values.
            - target_col_name (str, optional): When handling a mapping DataFrame, this is the column
            to check for duplicates. When None, assumes we're handling DataFrame columns directly.
        
        Returns:
            pd.DataFrame: DataFrame with resolved column duplications.
        """
        if target_col_name is not None:
            # Original behavior for handling mapping DataFrames
            # Duplicated subset
            duplicated_subset = df_or_mapping[df_or_mapping[target_col_name].duplicated()].copy()
            # Non-duplicated subset
            non_duplicated_subset = df_or_mapping[~df_or_mapping[target_col_name].duplicated()].copy()
            # Replace values in the duplicated columns by appending the field_name
            duplicated_subset[target_col_name] = df_or_mapping['name'] + ' - ' + df_or_mapping['field_name']
            # Combine the two subsets
            return pd.concat([non_duplicated_subset, duplicated_subset])
        else:
            # New behavior for handling DataFrame columns directly
            df = df_or_mapping.copy()
            # Find columns that have any duplicates at all
            duplicate_mask = df.columns.duplicated(keep=False)
            duplicated_col_names = df.columns[duplicate_mask].unique()
            
            if len(duplicated_col_names) > 0:
                # Create a new column mapping for rename operation
                new_columns = df.columns.tolist()
                
                for col_name in duplicated_col_names:
                    # Find all indices where this column name appears
                    indices = [i for i, name in enumerate(new_columns) if name == col_name]
                    
                    # Skip the first occurrence, only rename subsequent occurrences
                    for idx in indices[1:]:
                        new_col_name = f"_{col_name}"
                        # Check if the new name already exists or will be created
                        suffix_count = 1
                        while new_col_name in new_columns:
                            new_col_name = f"{'_' * (suffix_count + 1)}{col_name}"
                            suffix_count += 1
                        
                        # Update the name in our new_columns list
                        new_columns[idx] = new_col_name
                
                # Apply the renaming
                df.columns = new_columns
            

    def _handshake(self):
        """
        Khởi tạo kết nối cho phiên làm việc.
        Initiate handshake to establish a session.
        """
        url = 'https://trading.vietcap.com.vn/priceboard'
        try:
            session = requests.Session()
            session.headers.update(self.headers)
            session.get(url, timeout=10)
            # Cập nhật headers với cookies từ priceboard
            self.headers.update(session.cookies.get_dict())
        except Exception as e:
            if self.show_log:
                logger.warning(f"Handshake thất bại: {e}")

    def _get_ratio_dict(self, lang:str='vi', format:str='dict', style:str='readable', show_log: Optional[bool] = False) -> Union[pd.DataFrame, Dict]:
        """
        Lấy từ điển ánh xạ cho tất cả các chỉ số tài chính từ nguồn VCI microservices.

        Tham số:
            - lang (str): Ngôn ngữ của báo cáo ('vi' hoặc 'en'). Mặc định là 'vi'.
            - format (str): Định dạng trả về ('dict' hoặc 'dataframe'). Mặc định là 'dict'.
            - style (str): Phong cách tên cột ('readable' cho tên đầy đủ, 'code' cho mã kỹ thuật). Mặc định là 'readable'.
            - show_log (bool): Hiển thị thông tin log hoặc không. Mặc định là False.
            
        Returns:
            Union[pd.DataFrame, Dict]: Dữ liệu ánh xạ tùy theo tham số format.
        """
        # Validate lang
        if lang not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Ngôn ngữ '{lang}' không hợp lệ. Chỉ chấp nhận {', '.join(SUPPORTED_LANGUAGES)}.")

        url = f'{self.base_url}/v1/company/{self.symbol}/financial-statement/metrics'
        
        if show_log:
            logger.debug(f"Requesting financial ratio data from {url}")
        
        # Use api_client.send_request instead of direct requests
        response_data = client.send_request(
            url=url,
            headers=self.headers,
            method="GET",
            payload=None,
            show_log=show_log,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode
        )
        
        data = response_data.get('data')
        if data is None:
            raise ValueError(f"Không nhận được dữ liệu metadata từ VCI cho mã {self.symbol}.")

        combine_ls = []
        for key in data.keys():
            df = pd.DataFrame(data[key])
            df['report_name'] = key
            df = df[['report_name', 'field', 'parent', 'titleEn', 'titleVi', 'fullTitleVi', 'fullTitleEn']]
            combine_ls.append(df)

        df = pd.concat(combine_ls)
        df = df.rename(columns={'field': 'field_name', 'titleVi': 'name', 'titleEn': 'en_name', 'fullTitleVi': 'full_name', 'fullTitleEn': 'en_full_name'})

        if format == 'dict':
            if lang == 'vi':
                return df.set_index('field_name')['name'].to_dict()
            elif lang == 'en':
                return df.set_index('field_name')['en_name'].to_dict()
        else:
            return df

    def _get_report(self, report_type:Union[str, None] = None, lang: Optional[str] = 'en', 
                   show_log: Optional[bool] = False, 
                   mode: Optional[str] = 'final', 
                   style: Optional[str] = 'readable',
                   get_all: Optional[bool] = False,
                   period: Optional[str] = None,
                   limit: Optional[int] = None) -> pd.DataFrame:
        """
        Lấy dữ liệu báo cáo tài chính thô hoặc đã ánh xạ từ VCI REST API.
        """
        # Baseline limit
        effective_limit = limit if limit is not None else 4
        # Validate report_type
        if report_type not in _IQ_FINANCE_REPORT.keys():
            raise ValueError(f"Loại báo cáo tài chính không hợp lệ: '{report_type}'. Hỗ trợ: {', '.join(_IQ_FINANCE_REPORT.keys())}")
        
        report_section = _IQ_FINANCE_REPORT[report_type]
        
        if report_section == 'RATIO':
            url = f'{self.base_url}/v1/company/{self.symbol}/statistics-financial'
            params = {}
        else:
            url = f'{self.base_url}/v1/company/{self.symbol}/financial-statement'
            params = {"section": report_section}
        
        if show_log:
            logger.debug(f"Requesting financial report data from {url}. params: {params}")
        
        response_data = client.send_request(
            url=url,
            headers=self.headers,
            method="GET",
            params=params,
            payload=None,
            show_log=show_log,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode
        )
        
        data = response_data.get('data')
        if data is None:
            raise ValueError(f"Không nhận được dữ liệu (data) từ VCI cho mã {self.symbol} tại section {report_section}.")

        # Filter only requested period type
        effective_period = period if period else self.period
        # Map 'Y'/'Q' (internal) or 'year'/'quarter' (user) to VCI API keys
        target_key = 'years' if effective_period in ['year', 'Y'] else 'quarters'
        
        if report_section == 'RATIO':
            combined_df = pd.DataFrame(data)
        else:
            df_list = []
            # Only process the target period key from the response
            period_data = data.get(target_key, [])
            if period_data:
                combined_df = pd.DataFrame(period_data)
                # Keep tracking if it's year or quarter
                combined_df['report_period'] = target_key[:-1]
            else:
                combined_df = pd.DataFrame()

        # Apply limit
        if not combined_df.empty and len(combined_df) > effective_limit:
            combined_df = combined_df.head(effective_limit)

        if mode == 'final':
            return self._ratio_mapping(report_df=combined_df, lang=lang, style=style, get_all=get_all, show_log=show_log, period_type=effective_period)
        else:
            return combined_df

    def _ratio_mapping(self, report_df: pd.DataFrame, lang: Optional[str] = 'vi', style: str = 'readable', get_all: Optional[bool] = False, show_log: Optional[bool] = False, period_type: Optional[str] = None):
        # Get metadata mapping for both languages
        meta_df = self._get_ratio_dict(format='dataframe', show_log=show_log)
        vi_dict = meta_df.set_index('field_name')['name'].to_dict()
        en_dict = meta_df.set_index('field_name')['en_name'].to_dict()

        # Identify which columns are items vs metadata
        item_cols = [col for col in report_df.columns if col in vi_dict]
        
        # Create period labels if not already present
        if 'period' not in report_df.columns:
            # VCI logic for year/quarter
            y_col = 'year' if 'year' in report_df.columns else ('yearReport' if 'yearReport' in report_df.columns else None)
            q_col = 'quarter' if 'quarter' in report_df.columns else ('lengthReport' if 'lengthReport' in report_df.columns else None)
            
            if y_col and q_col:
                 def fmt_period(row):
                     try:
                         y = int(row[y_col])
                         q = int(row[q_col])
                         return f"{y}-Q{q}" if q < 5 and period_type in ['quarter', 'Q'] else f"{y}"
                     except:
                         return "N/A"
                 report_df['period'] = report_df.apply(fmt_period, axis=1)
            elif y_col:
                 report_df['period'] = report_df[y_col].astype(str)
            elif 'report_period' in report_df.columns:
                 report_df['period'] = report_df['report_period']
        
        # We want to return Items as rows and Periods as columns (match KBS)
        if 'period' in report_df.columns:
            # Drop metadata columns that are NOT the items or period
            cols_to_keep = ['period'] + item_cols
            processed_df = report_df[cols_to_keep].copy()
            
            # Set period as index then transpose
            processed_df = processed_df.set_index('period').T
            
            # Now Rows are our items (codes). Let's add readable labels.
            processed_df.index.name = 'item_id'
            processed_df = processed_df.reset_index()
            
            processed_df['item'] = processed_df['item_id'].map(vi_dict)
            processed_df['item_en'] = processed_df['item_id'].map(en_dict)
            
            # Reorder columns: metadata first, then periods
            period_cols = [c for c in processed_df.columns if c not in ['item', 'item_en', 'item_id']]
            # Use original order for columns
            processed_df = processed_df[['item', 'item_en', 'item_id'] + period_cols]
            
            return processed_df
        
        return report_df

    def _get_financial_report(self, report_type: str, period: Optional[str] = None, lang: Optional[str] = 'en', 
                             mode: Optional[str] = 'final', style: Optional[str] = 'readable',
                             get_all: Optional[bool] = False, dropna: Optional[bool] = True, 
                             show_log: Optional[bool] = False, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Cổng truy xuất báo cáo tài chính nội bộ.
        """
        df = self._get_report(report_type=report_type, lang=lang, mode=mode, style=style, 
                             get_all=get_all, show_log=show_log, limit=limit, period=period)
        
        if df.empty:
            return df

        # Filter by period if requested
        if period in ['year', 'quarter']:
             # This is a bit complex as REST returns multiple periods. 
             # For simplicity, we just filter the resulting df if 'report_period' exists
             pass
        
        if dropna:
            df = _safe_infer_objects(df.fillna(0))
            df = df.loc[:, (df != 0).any(axis=0)]
            
        return df

    def balance_sheet(self, period: Optional[str] = None, lang: Optional[str] = 'en', 
                    dropna: Optional[bool] = True, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Trích xuất dữ liệu bảng cân đối kế toán từ nguồn VCI REST API.

        Tham số:
            - period (str): Kỳ báo cáo ('year' hoặc 'quarter'). Mặc định lấy theo cấu hình khởi tạo.
            - lang (str): Ngôn ngữ ('vi' hoặc 'en'). Mặc định là 'en'.
            - dropna (bool): Loại bỏ các cột có tất cả giá trị bằng 0. Mặc định là True.
            - show_log (bool): Hiển thị thông tin log. Mặc định là False.

        Returns:
            pd.DataFrame: Bảng cân đối kế toán với chỉ mục là kỳ báo cáo.
        """
        return self._get_financial_report('balance_sheet', period=period, lang=lang, dropna=dropna, show_log=show_log)

    def income_statement(self, period: Optional[str] = None, lang: Optional[str] = 'en', 
                        dropna: Optional[bool] = True, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Trích xuất báo cáo kết quả kinh doanh từ nguồn VCI REST API.

        Tham số:
            - period (str): Kỳ báo cáo ('year' hoặc 'quarter').
            - lang (str): Ngôn ngữ ('vi' hoặc 'en').
            - dropna (bool): Loại bỏ các cột 0.
            - show_log (bool): Hiển thị log.

        Returns:
            pd.DataFrame: Báo cáo kết quả kinh doanh.
        """
        return self._get_financial_report('income_statement', period=period, lang=lang, dropna=dropna, show_log=show_log)

    def cash_flow(self, period: Optional[str] = None, lang: Optional[str] = 'en', 
                 dropna: Optional[bool] = True, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Trích xuất báo cáo lưu chuyển tiền tệ từ nguồn VCI REST API.

        Tham số:
            - period (str): Kỳ báo cáo ('year' hoặc 'quarter').
            - lang (str): Ngôn ngữ ('vi' hoặc 'en').
            - dropna (bool): Loại bỏ các cột 0.
            - show_log (bool): Hiển thị log.

        Returns:
            pd.DataFrame: Báo cáo lưu chuyển tiền tệ.
        """
        return self._get_financial_report('cash_flow', period=period, lang=lang, dropna=dropna, show_log=show_log)

    def ratio(self, period: Optional[str] = None, lang: Optional[str] = 'en', 
            dropna: Optional[bool] = True, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Trích xuất các chỉ số tài chính (Financial Ratios) từ nguồn VCI REST API.

        Tham số:
            - period (str): Kỳ báo cáo ('year' hoặc 'quarter').
            - lang (str): Ngôn ngữ ('vi' hoặc 'en').
            - dropna (bool): Loại bỏ các cột 0.
            - show_log (bool): Hiển thị log.

        Returns:
            pd.DataFrame: Bảng các chỉ số tài chính.
        """
        return self._get_financial_report('ratio', period=period, lang=lang, dropna=dropna, show_log=show_log)


# Register provider
from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401
ProviderRegistry.register('financial', 'vci', Finance)
