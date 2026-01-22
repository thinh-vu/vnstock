"""Financial module for KB Securities (KBS) data source."""

import json
import pandas as pd
from typing import Optional, List, Dict, Tuple, Union
from enum import Enum
from vnai import agg_execution
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.parser import get_asset_type, normalize_english_text_to_snake_case
from vnstock.core.utils.field import FieldHandler
from vnstock.core.utils.client import send_request, ProxyConfig
from vnstock.core.utils.user_agent import get_headers
from vnstock.explorer.kbs.const import (
    _SAS_FINANCE_INFO_URL,
    _INCOME_STATEMENT_MAP,
    _BALANCE_SHEET_MAP,
    _CASH_FLOW_MAP,
    _FINANCIAL_RATIOS_MAP,
    _FINANCIAL_REPORT_TYPE_MAP,
    _FINANCIAL_PERIOD_TYPE_MAP,
)

logger = get_logger(__name__)


class FieldDisplayMode(Enum):
    """Field display modes."""
    STD = "std"
    ALL = "all"
    AUTO = "auto"


class Finance:
    """
    Lớp truy cập dữ liệu tài chính từ KB Securities (KBS).
    """

    def __init__(
        self,
        symbol: str,
        random_agent: Optional[bool] = False,
        proxy_config: Optional[ProxyConfig] = None,
        show_log: Optional[bool] = False,
        standardize_columns: Optional[bool] = True,
        proxy_mode: Optional[str] = None,
        proxy_list: Optional[List[str]] = None,
    ):
        """
        Khởi tạo Finance client cho KBS.

        Args:
            symbol: Mã chứng khoán (VD: 'ACB', 'VNM').
            random_agent: Sử dụng user agent ngẫu nhiên. Mặc định False.
            proxy_config: Cấu hình proxy. Mặc định None.
            show_log: Hiển thị log debug. Mặc định False.
            standardize_columns: Chuẩn hoá tên cột theo schema. Mặc định True.
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
        self.standardize_columns = standardize_columns
        
        # Initialize field handler for advanced field processing
        # Don't pass reference_dir to avoid file loading warnings
        self.field_handler = FieldHandler(reference_dir=None, data_source='KBS')
        # Ensure mappings are loaded from built-in KBS mappings
        self.field_handler._load_reference_data('')
        
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

        # Set logger level based on show_log parameter
        if show_log:
            logger.setLevel('INFO')
        else:
            logger.setLevel('CRITICAL')

    def _get_column_mapping(self, report_type: str) -> Dict[str, str]:
        """
        Lấy column mapping cho loại báo cáo.
        
        Args:
            report_type: Loại báo cáo (income_statement, balance_sheet, cash_flow, financial_ratios)
            
        Returns:
            Dictionary chứa mapping từ cột gốc sang cột chuẩn hoá
        """
        mappings = {
            'income_statement': _INCOME_STATEMENT_MAP,
            'balance_sheet': _BALANCE_SHEET_MAP,
            'cash_flow': _CASH_FLOW_MAP,
            'financial_ratios': _FINANCIAL_RATIOS_MAP,
        }
        return mappings.get(report_type, {})
    
    def _parse_financial_response(self, response: Dict, report_key: str) -> pd.DataFrame:
        """
        Parse KBS API response and extract financial data with proper structure.
        
        Args:
            response: API response containing Audit, Unit, Head, Content
            report_key: Key in Content (e.g., 'Kết quả kinh doanh')
            
        Returns:
            DataFrame with proper financial data structure
        """
        # Extract components from response
        audit_list = response.get('Audit', [])
        unit_list = response.get('Unit', [])
        head_list = response.get('Head', [])
        content = response.get('Content', {})
        
        # Get the report data
        report_data = content.get(report_key, [])
        
        if not report_data:
            return pd.DataFrame()
        
        # Extract period information from Head
        # Head contains: YearPeriod, TermName, TermNameEN, AuditedStatus, ReportDate, etc.
        periods = []
        period_labels = []
        if head_list:
            for head in head_list:
                if isinstance(head, dict):
                    # Create standardized period label
                    year = head.get('YearPeriod', '')
                    term_name = head.get('TermName', '')
                    
                    # Parse quarter number from TermName (e.g., "Quý 1" -> "Q1")
                    if term_name and 'Quý' in term_name:
                        # Extract quarter number
                        quarter_num = term_name.replace('Quý', '').strip()
                        period_label = f"{year}-Q{quarter_num}"
                    else:
                        # Annual report - just use year
                        period_label = str(year)
                    
                    periods.append(period_label)
                    period_labels.append(period_label)
        
        # Extract audit status from Audit (maps AuditedStatusCode to Description)
        audit_status_map = {}
        if audit_list:
            for audit in audit_list:
                if isinstance(audit, dict):
                    code = audit.get('AuditedStatusCode')
                    desc = audit.get('Description')
                    if code and desc:
                        audit_status_map[code] = desc
        
        # Build DataFrame from report data
        rows = []
        item_id_counter = {}  # Track collisions
        
        for record in report_data:
            item = record.get('Name', '')
            item_en = record.get('NameEn', '')
            
            # Generate item_id using field handler
            if item_en and item_en.strip():
                item_id = self.field_handler.normalizer.normalize_field_name(item_en, language='en')
            elif item and item.strip():
                item_id = self.field_handler.normalizer.normalize_field_name(item, language='vi')
            else:
                item_id = ""
            
            # Handle collisions - append counter if duplicate
            if item_id and item_id in item_id_counter:
                item_id_counter[item_id] += 1
                item_id = f"{item_id}_{item_id_counter[item_id]}"
            elif item_id:
                item_id_counter[item_id] = 1
            
            row = {
                'item': item,
                'item_en': item_en,
                'item_id': item_id,
                'unit': record.get('Unit', ''),
                'levels': record.get('Levels', 0),
                'row_number': record.get('ID', 0),  # Use ID as row ordering (RowNumber is always None in API)
            }
            
            # Add period values (Value1, Value2, Value3, Value4)
            for i, period_label in enumerate(periods, 1):
                value_key = f'Value{i}'
                value = record.get(value_key)
                # Convert to numeric if possible
                if value is not None:
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        pass
                row[period_label] = value
            
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Reorder columns: metadata first, then periods
        metadata_cols = ['item', 'item_en', 'item_id', 'unit', 'levels', 'row_number']
        period_cols = periods
        df = df[metadata_cols + period_cols]
        
        # Add metadata
        df.attrs['audit_status_map'] = audit_status_map
        df.attrs['periods'] = periods
        df.attrs['report_key'] = report_key
        
        return df

    def _apply_schema_standardization(self, df: pd.DataFrame, report_type: str) -> pd.DataFrame:
        """
        Áp dụng chuẩn hoá schema cho DataFrame.
        
        Args:
            df: DataFrame cần chuẩn hoá
            report_type: Loại báo cáo
            
        Returns:
            DataFrame với cột chuẩn hoá
        """
        if not self.standardize_columns or df.empty:
            return df
        
        mapping = self._get_column_mapping(report_type)
        rename_dict = {old: new for old, new in mapping.items() if old in df.columns}
        
        if rename_dict:
            df = df.rename(columns=rename_dict)
            if self.show_log:
                logger.info(f'Applied schema standardization: {len(rename_dict)} columns renamed')
        
        return df
    
    def _filter_columns_by_lang(self, df: pd.DataFrame, display_mode: Optional[Union[str, FieldDisplayMode]] = FieldDisplayMode.STD) -> pd.DataFrame:
        """
        Filter DataFrame columns based on field display mode.
        
        Args:
            df: DataFrame to filter
            display_mode: Field display mode
                - FieldDisplayMode.STD: Keep only 'item' and 'item_id' columns (standardized)
                - FieldDisplayMode.ALL: Keep all item columns (item, item_en, item_id)
                - FieldDisplayMode.AUTO: Auto-convert based on data type
                - 'vi': Keep Vietnamese names only (backward compatibility)
                - 'en': Keep English names only (backward compatibility)
                - None: Keep all item columns (backward compatibility)
            
        Returns:
            DataFrame with filtered columns
        """
        if df.empty:
            return df
        
        # Convert string to enum for backward compatibility
        if isinstance(display_mode, str):
            if display_mode == 'vi':
                display_mode = FieldDisplayMode.STD
            elif display_mode == 'en':
                display_mode = FieldDisplayMode.STD
            else:
                display_mode = FieldDisplayMode.ALL
        
        # Get metadata columns (non-period columns)
        period_cols = df.attrs.get('periods', [])
        metadata_cols = [col for col in df.columns if col not in period_cols]
        
        # Create a copy to avoid SettingWithCopyWarning
        df_filtered = df.copy()
        
        if display_mode == FieldDisplayMode.ALL:
            # Keep all metadata columns
            cols_to_keep = metadata_cols
        elif display_mode == FieldDisplayMode.AUTO:
            # Auto-convert logic (for future implementation)
            cols_to_keep = metadata_cols
        else:  # STD
            # Keep only item and item_id columns
            cols_to_keep = [col for col in metadata_cols if col in ['item', 'item_id']]
            
            # Handle English preference (backward compatibility)
            if isinstance(display_mode, str) and display_mode == 'en' and 'item_en' in df_filtered.columns:
                df_filtered['item'] = df_filtered['item_en']
                cols_to_keep = ['item', 'item_id']
        
        # Add period columns
        cols_to_keep.extend(period_cols)
        
        # Filter to only existing columns
        cols_to_keep = [col for col in cols_to_keep if col in df_filtered.columns]
        
        return df_filtered[cols_to_keep]

    def _fetch_financial_data(
        self,
        report_type: str = 'KQKD',
        period_type: int = 1,
        page: int = 1,
        page_size: int = 4,
        show_log: Optional[bool] = False
    ) -> Dict:
        """
        Lấy dữ liệu tài chính từ API SAS với các tham số chính xác.

        Args:
            report_type: Loại báo cáo (CDKT, KQKD, LCTT, CSTC, CTKH, BCTT)
            period_type: Loại kỳ báo cáo (1=năm, 2=quý)
            page: Trang (mặc định 1)
            page_size: Số bản ghi trên trang (mặc định 4)
            show_log: Hiển thị log debug.

        Returns:
            Dictionary chứa dữ liệu tài chính đầy đủ.
        """
        url = f'{_SAS_FINANCE_INFO_URL}/{self.symbol}'
        
        # Build params based on report type
        # Note: API is case-sensitive and requires specific parameters per report type
        params = {
            'page': page,
            'pageSize': page_size,
            'type': report_type,
            'unit': 1000,  # Đơn vị ngàn đồng
            'termtype': period_type,  # 1=năm, 2=quý (lowercase!)
        }
        
        # Add languageid for most report types (except cash flow which uses termType)
        if report_type != 'LCTT':
            params['languageid'] = 1
        else:
            # Cash flow uses different parameter names
            params['code'] = self.symbol
            params['termType'] = period_type  # Cash flow uses camelCase termType

        # Log request configuration using logger
        if show_log or self.show_log:
            logger.info(f"KBS Financial API Request: {self.symbol} - {report_type} - Period: {period_type}")

        try:
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
            
            if show_log or self.show_log:
                if isinstance(json_data, dict) and 'data' in json_data:
                    logger.info(f"API Response received: {len(json_data.get('data', []))} records")
            
            return json_data
        except Exception as e:
            if show_log or self.show_log:
                logger.error(f"API Request Failed: {str(e)}")
            raise

    @agg_execution("KBS")
    def income_statement(
        self,
        period: str = 'year',
        display_mode: Optional[Union[str, FieldDisplayMode]] = FieldDisplayMode.STD,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Truy xuất báo cáo kết quả kinh doanh (income statement).

        Args:
            period: Loại kỳ báo cáo ('year' hoặc 'quarter'). Mặc định 'year'.
            display_mode: Chế độ hiển thị trường dữ liệu. Mặc định FieldDisplayMode.STD.
                - FieldDisplayMode.STD: Chỉ giữ cột 'item' và 'item_id' (đã chuẩn hóa)
                - FieldDisplayMode.ALL: Giữ tất cả cột item (item, item_en, item_id)
                - 'vi': Chỉ giữ tên tiếng Việt (tương thích ngược)
                - 'en': Chỉ giữ tên tiếng Anh (tương thích ngược)
                - None: Giữ tất cả cột (tương thích ngược)
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa báo cáo kết quả kinh doanh.

        Examples:
            >>> finance = Finance('ACB')
            >>> df = finance.income_statement(period='year', display_mode=FieldDisplayMode.STD)
            >>> # Returns DataFrame with columns: item, item_id, unit, periods...
            >>> df_all = finance.income_statement(period='year', display_mode=FieldDisplayMode.ALL)
            >>> # Returns DataFrame with all item columns
            >>> # Backward compatibility:
            >>> df_vi = finance.income_statement(period='year', display_mode='vi')
            >>> df_en = finance.income_statement(period='year', display_mode='en')
        """
        # Map period to termType (1=year, 2=quarter)
        period_type = 1 if period == 'year' else 2
        
        # Fetch data with correct API parameters
        financial_data = self._fetch_financial_data(
            report_type='KQKD',
            period_type=period_type,
            show_log=show_log
        )

        if not financial_data:
            raise ValueError(
                f"Không tìm thấy dữ liệu tài chính cho mã {self.symbol}."
            )

        # Parse financial response with proper structure
        df = self._parse_financial_response(financial_data, 'Kết quả kinh doanh')
        
        if df.empty:
            logger.warning(f"Không tìm thấy báo cáo kết quả kinh doanh cho {self.symbol}.")
            return pd.DataFrame()

        # Apply schema standardization if enabled
        if self.standardize_columns:
            df = self._apply_schema_standardization(df, 'income_statement')

        # Filter columns by display mode
        df = self._filter_columns_by_lang(df, display_mode)

        # Add metadata
        df.attrs['symbol'] = self.symbol
        df.attrs['source'] = self.data_source
        df.attrs['report_type'] = 'income_statement'
        df.attrs['period'] = period

        if show_log or self.show_log:
            logger.info(
                f'Truy xuất thành công báo cáo kết quả kinh doanh cho {self.symbol}.'
            )

        return df

    @agg_execution("KBS")
    def balance_sheet(
        self,
        period: str = 'year',
        display_mode: Optional[Union[str, FieldDisplayMode]] = FieldDisplayMode.STD,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Truy xuất bảng cân đối kế toán (balance sheet).

        Args:
            period: Loại kỳ báo cáo ('year' hoặc 'quarter'). Mặc định 'year'.
            display_mode: Chế độ hiển thị trường dữ liệu. Mặc định FieldDisplayMode.STD.
                - FieldDisplayMode.STD: Chỉ giữ cột 'item' và 'item_id' (đã chuẩn hóa)
                - FieldDisplayMode.ALL: Giữ tất cả cột item (item, item_en, item_id)
                - 'vi': Chỉ giữ tên tiếng Việt (tương thích ngược)
                - 'en': Chỉ giữ tên tiếng Anh (tương thích ngược)
                - None: Giữ tất cả cột (tương thích ngược)
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa bảng cân đối kế toán.

        Examples:
            >>> finance = Finance('ACB')
            >>> df = finance.balance_sheet(period='year', display_mode=FieldDisplayMode.STD)
            >>> df_all = finance.balance_sheet(period='year', display_mode=FieldDisplayMode.ALL)
            >>> # Backward compatibility:
            >>> df_vi = finance.balance_sheet(period='year', display_mode='vi')
            >>> df_en = finance.balance_sheet(period='year', display_mode='en')
        """
        # Map period to termType (1=year, 2=quarter)
        period_type = 1 if period == 'year' else 2
        
        # Fetch data with correct API parameters
        financial_data = self._fetch_financial_data(
            report_type='CDKT',
            period_type=period_type,
            show_log=show_log
        )

        if not financial_data:
            raise ValueError(
                f"Không tìm thấy dữ liệu tài chính cho mã {self.symbol}."
            )

        # Parse financial response with proper structure
        # Note: API uses 'Cân đối kế toán' not 'Bảng cân đối kế toán'
        df = self._parse_financial_response(financial_data, 'Cân đối kế toán')
        
        if df.empty:
            logger.warning(f"Không tìm thấy bảng cân đối kế toán cho {self.symbol}.")
            return pd.DataFrame()

        # Apply schema standardization if enabled
        if self.standardize_columns:
            df = self._apply_schema_standardization(df, 'balance_sheet')

        # Filter columns by display mode
        df = self._filter_columns_by_lang(df, display_mode)

        # Add metadata
        df.attrs['symbol'] = self.symbol
        df.attrs['source'] = self.data_source
        df.attrs['report_type'] = 'balance_sheet'
        df.attrs['period'] = period

        if show_log or self.show_log:
            logger.info(
                f'Truy xuất thành công bảng cân đối kế toán cho {self.symbol}.'
            )

        return df

    @agg_execution("KBS")
    def cash_flow(
        self,
        period: str = 'year',
        display_mode: Optional[Union[str, FieldDisplayMode]] = FieldDisplayMode.STD,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Truy xuất báo cáo lưu chuyển tiền tệ (cash flow statement).

        Args:
            period: Loại kỳ báo cáo ('year' hoặc 'quarter'). Mặc định 'year'.
            display_mode: Chế độ hiển thị trường dữ liệu. Mặc định FieldDisplayMode.STD.
                - FieldDisplayMode.STD: Chỉ giữ cột 'item' và 'item_id' (đã chuẩn hóa)
                - FieldDisplayMode.ALL: Giữ tất cả cột item (item, item_en, item_id)
                - 'vi': Chỉ giữ tên tiếng Việt (tương thích ngược)
                - 'en': Chỉ giữ tên tiếng Anh (tương thích ngược)
                - None: Giữ tất cả cột (tương thích ngược)
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa báo cáo lưu chuyển tiền tệ.

        Examples:
            >>> finance = Finance('ACB')
            >>> df = finance.cash_flow(period='year', display_mode=FieldDisplayMode.STD)
            >>> df_all = finance.cash_flow(period='year', display_mode=FieldDisplayMode.ALL)
            >>> # Backward compatibility:
            >>> df_vi = finance.cash_flow(period='year', display_mode='vi')
            >>> df_en = finance.cash_flow(period='year', display_mode='en')
        """
        # Map period to termType (1=year, 2=quarter)
        period_type = 1 if period == 'year' else 2
        
        # Fetch data with correct API parameters
        financial_data = self._fetch_financial_data(
            report_type='LCTT',
            period_type=period_type,
            show_log=show_log
        )

        if not financial_data:
            raise ValueError(
                f"Không tìm thấy dữ liệu tài chính cho mã {self.symbol}."
            )

        # Parse financial response with proper structure
        # Note: API has two cash flow types - try indirect first (more common), then direct
        content = financial_data.get('Content', {})
        
        # Try indirect cash flow first (most common)
        cash_flow_key = None
        if 'Lưu chuyển tiền tệ gián tiếp' in content:
            cash_flow_key = 'Lưu chuyển tiền tệ gián tiếp'
        elif 'Lưu chuyển tiền tệ trực tiếp' in content:
            cash_flow_key = 'Lưu chuyển tiền tệ trực tiếp'
        
        if not cash_flow_key:
            logger.warning(f"Không tìm thấy báo cáo lưu chuyển tiền tệ cho {self.symbol}.")
            return pd.DataFrame()
        
        df = self._parse_financial_response(financial_data, cash_flow_key)
        
        if df.empty:
            logger.warning(f"Không tìm thấy báo cáo lưu chuyển tiền tệ cho {self.symbol}.")
            return pd.DataFrame()

        # Apply schema standardization if enabled
        if self.standardize_columns:
            df = self._apply_schema_standardization(df, 'cash_flow')

        # Filter columns by display mode
        df = self._filter_columns_by_lang(df, display_mode)

        # Add metadata
        df.attrs['symbol'] = self.symbol
        df.attrs['source'] = self.data_source
        df.attrs['report_type'] = 'cash_flow'
        df.attrs['period'] = period

        if show_log or self.show_log:
            logger.info(
                f'Truy xuất thành công báo cáo lưu chuyển tiền tệ cho {self.symbol}.'
            )

        return df

    @agg_execution("KBS")
    def ratio(
        self,
        period: str = 'year',
        display_mode: Optional[Union[str, FieldDisplayMode]] = FieldDisplayMode.STD,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Truy xuất các chỉ số tài chính (financial ratios).

        Args:
            period: Loại kỳ báo cáo ('year' hoặc 'quarter'). Mặc định 'year'.
            display_mode: Chế độ hiển thị trường dữ liệu. Mặc định FieldDisplayMode.STD.
                - FieldDisplayMode.STD: Chỉ giữ cột 'item' và 'item_id' (đã chuẩn hóa)
                - FieldDisplayMode.ALL: Giữ tất cả cột item (item, item_en, item_id)
                - 'vi': Chỉ giữ tên tiếng Việt (tương thích ngược)
                - 'en': Chỉ giữ tên tiếng Anh (tương thích ngược)
                - None: Giữ tất cả cột (tương thích ngược)
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa các chỉ số tài chính.

        Examples:
            >>> finance = Finance('ACB')
            >>> df = finance.ratio(period='year', display_mode=FieldDisplayMode.STD)
            >>> df_all = finance.ratio(period='year', display_mode=FieldDisplayMode.ALL)
            >>> # Backward compatibility:
            >>> df_vi = finance.ratio(period='year', display_mode='vi')
            >>> df_en = finance.ratio(period='year', display_mode='en')
        """
        # Map period to termType (1=year, 2=quarter)
        period_type = 1 if period == 'year' else 2
        
        # Fetch data with correct API parameters
        financial_data = self._fetch_financial_data(
            report_type='CSTC',
            period_type=period_type,
            show_log=show_log
        )

        if not financial_data:
            raise ValueError(
                f"Không tìm thấy dữ liệu tài chính cho mã {self.symbol}."
            )

        # Parse financial response with proper structure
        # Note: API returns multiple ratio groups, combine them all
        content = financial_data.get('Content', {})
        
        # Ratio groups in the API response
        ratio_groups = [
            'Nhóm chỉ số Định giá',  # Valuation ratios
            'Nhóm chỉ số Sinh lợi',  # Profitability ratios
            'Nhóm chỉ số Tăng trưởng',  # Growth ratios
            'Nhóm chỉ số Thanh khoản',  # Liquidity ratios
            'Nhóm chỉ số Chất lượng tài sản'  # Asset quality ratios
        ]
        
        # Collect all ratio data from all groups
        all_ratio_data = []
        for group_key in ratio_groups:
            group_data = content.get(group_key, [])
            if group_data:
                all_ratio_data.extend(group_data)
        
        if not all_ratio_data:
            logger.warning(f"Không tìm thấy chỉ số tài chính cho {self.symbol}.")
            return pd.DataFrame()
        
        # Extract components from response for proper parsing
        audit_list = financial_data.get('Audit', [])
        head_list = financial_data.get('Head', [])
        
        # Extract period information from Head
        periods = []
        if head_list:
            for head in head_list:
                if isinstance(head, dict):
                    year = head.get('YearPeriod', '')
                    term_name = head.get('TermName', '')
                    
                    # Parse quarter number from TermName (e.g., "Quý 1" -> "Q1")
                    if term_name and 'Quý' in term_name:
                        # Extract quarter number
                        quarter_num = term_name.replace('Quý', '').strip()
                        period_label = f"{year}-Q{quarter_num}"
                    else:
                        # Annual report - just use year
                        period_label = str(year)
                    
                    periods.append(period_label)
        
        # Extract audit status from Audit
        audit_status_map = {}
        if audit_list:
            for audit in audit_list:
                if isinstance(audit, dict):
                    code = audit.get('AuditedStatusCode')
                    desc = audit.get('Description')
                    if code and desc:
                        audit_status_map[code] = desc
        
        # Build DataFrame from ratio data
        rows = []
        item_id_counter = {}  # Track collisions
        
        for record in all_ratio_data:
            item = record.get('Name', '')
            item_en = record.get('NameEn', '')
            
            # Generate item_id using field handler
            if item_en and item_en.strip():
                item_id = self.field_handler.normalizer.normalize_field_name(item_en, language='en')
            elif item and item.strip():
                item_id = self.field_handler.normalizer.normalize_field_name(item, language='vi')
            else:
                item_id = ""
            
            # Handle collisions - append counter if duplicate
            if item_id and item_id in item_id_counter:
                item_id_counter[item_id] += 1
                item_id = f"{item_id}_{item_id_counter[item_id]}"
            elif item_id:
                item_id_counter[item_id] = 1
            
            row = {
                'item': item,
                'item_en': item_en,
                'item_id': item_id,
                'unit': record.get('Unit', ''),
                'levels': record.get('Levels', 0),
                'row_number': record.get('ID', 0),  # Use ID as row ordering (RowNumber is always None in API)
            }
            
            # Add period values
            for i, period_label in enumerate(periods, 1):
                value_key = f'Value{i}'
                value = record.get(value_key)
                if value is not None:
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        pass
                row[period_label] = value
            
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Reorder columns: metadata first, then periods
        metadata_cols = ['item', 'item_en', 'item_id', 'unit', 'levels', 'row_number']
        period_cols = periods
        df = df[metadata_cols + period_cols]
        
        df.attrs['audit_status_map'] = audit_status_map
        df.attrs['periods'] = periods
        df.attrs['report_key'] = 'Financial Ratios'
        
        if df.empty:
            logger.warning(f"Không tìm thấy chỉ số tài chính cho {self.symbol}.")
            return pd.DataFrame()

        # Apply schema standardization if enabled
        if self.standardize_columns:
            df = self._apply_schema_standardization(df, 'financial_ratios')

        # Filter columns by display mode
        df = self._filter_columns_by_lang(df, display_mode)

        # Add metadata
        df.attrs['symbol'] = self.symbol
        df.attrs['source'] = self.data_source
        df.attrs['report_type'] = 'financial_ratios'
        df.attrs['period'] = period

        if show_log or self.show_log:
            logger.info(f'Truy xuất thành công chỉ số tài chính cho {self.symbol}.')

        return df


# Register KBS Financial provider
from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401
ProviderRegistry.register('financial', 'kbs', Finance)
