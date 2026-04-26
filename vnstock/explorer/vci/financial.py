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
from vnai import optimize_execution
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
            
            return df
    
    def _handshake(self):
        """
        Phát động handshake để khởi tạo session và tránh bị chặn từ phía VCI.
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
                   get_all: Optional[bool] = False) -> pd.DataFrame:
        """
        Lấy dữ liệu báo cáo tài chính thô hoặc đã ánh xạ từ VCI REST API.

        Tham số:
            - report_type (str): Loại báo cáo ('income_statement', 'balance_sheet', 'cash_flow', 'ratio').
            - lang (str): Ngôn ngữ của báo cáo. Mặc định là 'en'.
            - show_log (bool): Hiển thị thông tin log hoặc không. Mặc định là False.
            - mode (str): Chế độ ('final' cho dữ liệu đã ánh xạ, 'raw' cho dữ liệu thô). Mặc định là 'final'.
            - style (str): Phong cách tên cột. Mặc định là 'readable'.
            - get_all (bool): Trả về tất cả các trường dữ liệu. Mặc định là False.

        Returns:
            pd.DataFrame: Dữ liệu báo cáo tài chính.
        """
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

        if report_section == 'RATIO':
            combined_df = pd.DataFrame(data)
        else:
            df_list = []
            for period_key, period_data in data.items():
                if period_data:
                    df = pd.DataFrame(period_data)
                    df['report_period'] = period_key[:-1] # Remove 's' from 'quarters'
                    df_list.append(df)
            if not df_list:
                return pd.DataFrame()
            combined_df = pd.concat(df_list, ignore_index=True)

        if mode == 'final':
            return self._ratio_mapping(report_df=combined_df, lang=lang, style=style, get_all=get_all, show_log=show_log)
        else:
            return combined_df

    def _ratio_mapping(self, report_df: pd.DataFrame, lang: Optional[str] = 'vi', style: str = 'readable', get_all: Optional[bool] = False, show_log: Optional[bool] = False):
        """
        Ánh xạ các mã trường kỹ thuật sang tên hiển thị dễ đọc dựa trên metadata.

        Tham số:
            - report_df (pd.DataFrame): DataFrame dữ liệu thô.
            - lang (str): Ngôn ngữ ánh xạ.
            - style (str): Phong cách lấy tên.
            - get_all (bool): Giữ lại tất cả các cột.
            - show_log (bool): Hiển thị log.
        """
        ratio_dict = self._get_ratio_dict(lang=lang, style=style, format='dict')

        report_df.columns = [ratio_dict[col] if col in ratio_dict else col for col in report_df.columns]
        
        # Add Tahun/Quarter labels
        if 'year' in report_df.columns:
            report_df['yearReport'] = report_df['year']
        if 'quarter' in report_df.columns:
            report_df['lengthReport'] = report_df['quarter']

        # Construct a clean 'period' (Year-Q) if possible
        if 'year' in report_df.columns and 'quarter' in report_df.columns:
             report_df['period'] = report_df.apply(lambda x: f"{int(x['year'])}-Q{int(x['quarter'])}" if int(x['quarter']) < 5 else f"{int(x['year'])}", axis=1)
        elif 'year' in report_df.columns:
             report_df['period'] = report_df['year'].astype(str)

        # Standardize labels based on lang
        if lang == 'vi':
            if style == 'readable':
                 report_df = report_df.rename(columns={'period': 'Kỳ báo cáo', 'ticker': 'Mã CP'})
            index_name = 'Kỳ báo cáo'
        else:
            index_name = 'period'
        
        if 'period' in report_df.columns:
            report_df = report_df.set_index(index_name if lang == 'vi' and style == 'readable' else 'period')

        # Reorder and drop técnico columns
        if get_all == False:
            import re
            code_pattern = re.compile(r'^[a-z]{2,3}\d+$', re.IGNORECASE)
            cols_to_drop = ['year', 'quarter', 'yearReport', 'lengthReport', 'report_period', 'organCode', 'createDate', 'updateDate', 'publicDate']
            cols_to_drop += [col for col in report_df.columns if code_pattern.match(str(col))]
            report_df = report_df.drop(columns=[c for c in cols_to_drop if c in report_df.columns])
        
        return report_df

    def _get_financial_report(self, report_type: str, period: Optional[str] = None, lang: Optional[str] = 'en', 
                             mode: Optional[str] = 'final', style: Optional[str] = 'readable',
                             get_all: Optional[bool] = False, dropna: Optional[bool] = True, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Cổng truy xuất báo cáo tài chính nội bộ, xử lý lọc dữ liệu và định dạng.

        Tham số:
            - report_type (str): Key loại báo cáo.
            - period (str): Kỳ báo cáo (không bắt buộc).
            - lang (str): Ngôn ngữ.
            - mode (str): Chế độ xử lý.
            - style (str): Định dạng cột.
            - get_all (bool): Lấy tất cả cột.
            - dropna (bool): Loại bỏ cột rỗng.
            - show_log (bool): Hiển thị log.
        """
        df = self._get_report(report_type=report_type, lang=lang, mode=mode, style=style, get_all=get_all, show_log=show_log)
        
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

    @optimize_execution("VCI")
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

    @optimize_execution("VCI")
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

    @optimize_execution("VCI")
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

    @optimize_execution("VCI")
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
