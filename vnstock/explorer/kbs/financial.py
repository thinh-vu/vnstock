"""Financial module for KB Securities (KBS) data source."""

from enum import Enum
from typing import Dict, List, Optional, Union

import pandas as pd
from vnai import optimize_execution

from vnstock.core.utils.client import ProxyConfig, send_request
from vnstock.core.utils.field import FieldHandler
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.parser import get_asset_type
from vnstock.core.utils.user_agent import get_headers
from vnstock.explorer.kbs.const import (
    _BALANCE_SHEET_MAP,
    _CASH_FLOW_MAP,
    _FINANCIAL_RATIOS_MAP,
    _INCOME_STATEMENT_MAP,
    _SAS_FINANCE_INFO_URL,
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
        period: Optional[str] = None,
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
            period: Kỳ báo cáo mặc định ('year', 'quarter' hoặc None).
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

        # Validate input for period
        if period is not None and period not in ["year", "quarter"]:
            raise ValueError(
                "Kỳ báo cáo tài chính không hợp lệ. Chỉ chấp nhận 'year' hoặc 'quarter' hoặc None."
            )
        self.period = period

        # Validate if symbol is a stock
        if self.asset_type not in ["stock"]:
            raise ValueError("Mã CK không hợp lệ hoặc không phải cổ phiếu.")

        self.data_source = "KBS"
        self.headers = get_headers(
            data_source=self.data_source, random_agent=random_agent
        )
        self.show_log = show_log
        self.standardize_columns = standardize_columns

        # Initialize field handler for advanced field processing
        self.field_handler = FieldHandler(data_source="KBS")

        # Handle proxy configuration
        if proxy_config is None:
            # Create ProxyConfig from individual arguments
            p_mode = proxy_mode if proxy_mode else "try"
            # If user provides list, set request_mode to PROXY
            req_mode = "direct"
            if proxy_list and len(proxy_list) > 0:
                req_mode = "proxy"

            self.proxy_config = ProxyConfig(
                proxy_mode=p_mode, proxy_list=proxy_list, request_mode=req_mode
            )
        else:
            self.proxy_config = proxy_config

        # Set logger level based on show_log parameter
        if show_log:
            logger.setLevel("INFO")
        else:
            logger.setLevel("CRITICAL")

    def _get_column_mapping(self, report_type: str) -> Dict[str, str]:
        """
        Lấy column mapping cho loại báo cáo.

        Args:
            report_type: Loại báo cáo (income_statement, balance_sheet, cash_flow, financial_ratios)

        Returns:
            Dictionary chứa mapping từ cột gốc sang cột chuẩn hoá
        """  # noqa: W293
        mappings = {
            "income_statement": _INCOME_STATEMENT_MAP,
            "balance_sheet": _BALANCE_SHEET_MAP,
            "cash_flow": _CASH_FLOW_MAP,
            "financial_ratios": _FINANCIAL_RATIOS_MAP,
        }
        return mappings.get(report_type, {})

    def _parse_financial_response(
        self,
        response: Dict,
        report_key: str,
        include_metadata: bool = False,
        unit_multiplier: float = 1.0,
    ) -> pd.DataFrame:
        """
        Parse KBS API response and extract financial data with proper structure.

        Args:
            response: API response containing Audit, Unit, Head, Content
            report_key: Key in Content (e.g., 'Kết quả kinh doanh')
            include_metadata: Whether to include Audit and Unit info as rows in DataFrame
            unit_multiplier: Multiplier to apply to values (e.g. 1000.0)

        Returns:
            DataFrame with proper financial data structure
        """  # noqa: W293
        # Extract components from response
        audit_list = response.get("Audit", [])
        unit_list = response.get("Unit", [])
        head_list = response.get("Head", [])
        content = response.get("Content", {})

        # Get the report data
        report_data = content.get(report_key, [])

        if not report_data:
            return pd.DataFrame()

        # Extract period information from Head
        # Head contains: YearPeriod, TermName, TermNameEN, AuditedStatus, ReportDate, etc.
        periods = []
        period_audit_map = {}
        period_unit_map = {}

        if head_list:
            # Sort head_list by ID to ensure correct period order (API returns most recent first, we want chronological or consistent)
            # Actually ID usually reflects the order in Head
            sorted_head_list = sorted(head_list, key=lambda x: x.get("ID", 0))
            for head in sorted_head_list:
                if isinstance(head, dict):
                    # Create standardized period label
                    year = head.get("YearPeriod", "")
                    term_name = head.get("TermName", "")

                    # Parse quarter number from TermName (e.g., "Quý 1" -> "Q1")
                    if term_name and "Quý" in term_name:
                        # Extract quarter number
                        quarter_num = term_name.replace("Quý", "").strip()
                        period_label = f"{year}-Q{quarter_num}"
                    else:
                        if self.period == "quarter":
                            period_label = (
                                f"{year}-{term_name}" if term_name else str(year)
                            )
                        else:
                            period_label = str(year)

                    # Ensure period labels are unique
                    original_label = period_label
                    suffix = 1
                    while period_label in periods:
                        period_label = f"{original_label}_{suffix}"
                        suffix += 1

                    periods.append(period_label)

                    # Store audit/unit codes for this period
                    period_audit_map[period_label] = head.get("AuditedStatus", "")
                    period_unit_map[period_label] = head.get("United", "")

        # Extract mappings
        audit_desc_map = {}
        if audit_list:
            for audit in audit_list:
                if isinstance(audit, dict):
                    audit_desc_map[audit.get("AuditedStatusCode")] = audit.get(
                        "Description"
                    )

        unit_desc_map = {}
        if unit_list:
            for unit in unit_list:
                if isinstance(unit, dict):
                    unit_desc_map[unit.get("UnitedCode")] = unit.get("UnitedName")

        # Build DataFrame from report data
        rows = []
        item_id_counter = {}  # Track collisions

        for record in report_data:
            item = record.get("Name", "")
            item_en = record.get("NameEn", "")

            # Generate item_id using field handler
            if item_en and item_en.strip():
                item_id = self.field_handler.normalize_field_name(item_en)
            elif item and item.strip():
                item_id = self.field_handler.normalize_field_name(item)
            else:
                item_id = ""

            # Handle collisions - append counter if duplicate
            if item_id and item_id in item_id_counter:
                item_id_counter[item_id] += 1
                item_id = f"{item_id}_{item_id_counter[item_id]}"
            elif item_id:
                item_id_counter[item_id] = 1

            row = {
                "item": item,
                "item_en": item_en,
                "item_id": item_id,
                "unit": record.get("Unit", ""),
                "levels": record.get("Levels", 0),
                "row_number": record.get(
                    "ID", 0
                ),  # Use ID as row ordering (RowNumber is always None in API)
            }

            # Add period values (Value1, Value2, Value3, Value4...)
            # Note: API returns Value1, Value2... corresponding to the order in Head (ID 1, 2, 3, 4)
            # Since we sorted head_list by ID, periods[i] matches Value{i+1}
            for i, period_label in enumerate(periods, 1):
                value_key = f"Value{i}"
                value = record.get(value_key)
                # Convert to numeric if possible
                if value is not None:
                    try:
                        value = float(value) * unit_multiplier
                    except (ValueError, TypeError):
                        pass
                row[period_label] = value

            rows.append(row)

        # Add metadata rows if requested
        if include_metadata:
            # Audit Status Row
            audit_row = {
                "item": "Kiểm toán",
                "item_en": "Audit Status",
                "item_id": "audit_status",
                "unit": "",
                "levels": 0,
                "row_number": -2,
            }
            # Unit Type Row
            unit_row = {
                "item": "Đơn vị",
                "item_en": "Unit Type",
                "item_id": "unit_type",
                "unit": "",
                "levels": 0,
                "row_number": -1,
            }

            for period in periods:
                # Resolve Audit Status
                a_code = period_audit_map.get(period)
                audit_row[period] = audit_desc_map.get(a_code, a_code)

                # Resolve Unit Type
                u_code = period_unit_map.get(period)
                unit_row[period] = unit_desc_map.get(u_code, u_code)

            rows.append(audit_row)
            rows.append(unit_row)

        df = pd.DataFrame(rows)

        # Reorder columns: metadata first, then periods
        metadata_cols = ["item", "item_en", "item_id", "unit", "levels", "row_number"]

        # Filter columns to only those that exist
        existing_cols = [c for c in metadata_cols if c in df.columns]
        period_cols_existing = [c for c in periods if c in df.columns]

        # Filter out periods that have no data (all null)
        valid_period_cols = []
        for col in period_cols_existing:
            if not df[col].isnull().all():
                valid_period_cols.append(col)

        df = df[existing_cols + valid_period_cols]

        # Add metadata attributes
        final_periods = valid_period_cols
        df.attrs["audit_status"] = {
            p: audit_desc_map.get(c, c)
            for p, c in period_audit_map.items()
            if p in final_periods
        }
        df.attrs["unit_type"] = {
            p: unit_desc_map.get(c, c)
            for p, c in period_unit_map.items()
            if p in final_periods
        }
        df.attrs["periods"] = final_periods
        df.attrs["report_key"] = report_key

        return df

    def _fetch_series_data(
        self,
        report_type: str,
        period_type: int,
        report_key: str,
        limit: Optional[int] = None,
        include_metadata: bool = False,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Helper to fetch data across multiple pages to satisfy the limit.
        """
        # Baseline limit
        effective_limit = limit if limit is not None else 4

        dfs = []
        collected_periods = set()
        page = 1

        request_page_size = 4

        while len(collected_periods) < effective_limit:
            data = self._fetch_financial_data(
                report_type=report_type,
                period_type=period_type,
                page=page,
                page_size=request_page_size,
                show_log=show_log,
            )

            df = self._parse_financial_response(
                data,
                report_key,
                include_metadata=include_metadata,
                unit_multiplier=1000.0,
            )

            if df.empty:
                break

            new_periods = df.attrs.get("periods", [])
            if not new_periods:
                break

            # Filter out periods we already have
            actual_new_periods = [p for p in new_periods if p not in collected_periods]
            if not actual_new_periods:
                # If we got data but no new periods, it's likely we've looped or reached end
                break

            # If some periods are repeats, we only keep the new ones in this DF
            if len(actual_new_periods) < len(new_periods):
                cols_to_keep = [
                    c
                    for c in df.columns
                    if c not in new_periods or c in actual_new_periods
                ]
                df = df[cols_to_keep]
                df.attrs["periods"] = actual_new_periods

            dfs.append(df)
            collected_periods.update(actual_new_periods)

            page += 1
            if page > 20:
                break

        if not dfs:
            return pd.DataFrame()

        # Merge DataFrames
        final_df = dfs[0]

        for i in range(1, len(dfs)):
            next_df = dfs[i]
            next_periods = next_df.attrs.get("periods", [])

            # Merge on item_id.
            cols_to_merge = ["item_id"] + next_periods

            if "item_id" in next_df.columns:
                # Capture current attributes
                current_attrs = final_df.attrs

                # Use outer join to keep all items, but assume item names/metadata are consistent
                # Drop existing metadata from next_df to avoid duplicate columns (_x, _y)
                final_df = pd.merge(
                    final_df, next_df[cols_to_merge], on="item_id", how="outer"
                )

                # Update attributes
                current_attrs["periods"].extend(next_periods)
                if "audit_status" in next_df.attrs:
                    current_attrs["audit_status"].update(next_df.attrs["audit_status"])
                if "unit_type" in next_df.attrs:
                    current_attrs["unit_type"].update(next_df.attrs["unit_type"])

                final_df.attrs = current_attrs

        # Truncate to limit if we got more than requested (capped by effective_limit)
        all_periods = final_df.attrs.get("periods", [])
        if len(all_periods) > effective_limit:
            kept_periods = all_periods[:effective_limit]
            drop_periods = [p for p in all_periods if p not in kept_periods]
            final_df = final_df.drop(columns=drop_periods, errors="ignore")
            final_df.attrs["periods"] = kept_periods

        return final_df

    def _apply_schema_standardization(
        self, df: pd.DataFrame, report_type: str
    ) -> pd.DataFrame:
        """
        Áp dụng chuẩn hoá schema cho DataFrame.

        Args:
            df: DataFrame cần chuẩn hoá
            report_type: Loại báo cáo

        Returns:
            DataFrame với cột chuẩn hoá
        """  # noqa: W293
        if not self.standardize_columns or df.empty:
            return df

        mapping = self._get_column_mapping(report_type)

        if "item_id" in df.columns and mapping:
            # Replace mapped strings in item_id
            mask = df["item_id"].isin(mapping.keys())
            count = mask.sum()
            if count > 0:
                df["item_id"] = df["item_id"].replace(mapping)
                if self.show_log:
                    logger.info(
                        f"Applied schema standardization: {count} items standardized"
                    )

        return df

    def _filter_columns_by_lang(
        self,
        df: pd.DataFrame,
        display_mode: Optional[Union[str, FieldDisplayMode]] = FieldDisplayMode.STD,
    ) -> pd.DataFrame:
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
        """  # noqa: W293
        if df.empty:
            return df

        # Convert string to enum for backward compatibility
        if isinstance(display_mode, str):
            if display_mode == "vi":
                display_mode = FieldDisplayMode.STD
            elif display_mode == "en":
                display_mode = FieldDisplayMode.STD
            else:
                display_mode = FieldDisplayMode.ALL

        # Get metadata columns (non-period columns)
        period_cols = df.attrs.get("periods", [])
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
            cols_to_keep = [col for col in metadata_cols if col in ["item", "item_id"]]

            # Handle English preference (backward compatibility)
            if (
                isinstance(display_mode, str)
                and display_mode == "en"
                and "item_en" in df_filtered.columns
            ):
                df_filtered["item"] = df_filtered["item_en"]
                cols_to_keep = ["item", "item_id"]

        # Add period columns
        cols_to_keep.extend(period_cols)

        # Filter to only existing columns
        cols_to_keep = [col for col in cols_to_keep if col in df_filtered.columns]

        return df_filtered[cols_to_keep]

    def _fetch_financial_data(
        self,
        report_type: str = "KQKD",
        period_type: int = 1,
        page: int = 1,
        page_size: int = 4,
        show_log: Optional[bool] = False,
    ) -> Dict:
        """
        Lấy dữ liệu tài chính từ API SAS với các tham số chính xác.

        Args:
            report_type: Loại báo cáo (CDKT, KQKD, LCTT, CSTC, CTKH, BCTT)
            period_type: Loại kỳ báo cáo (1=năm, 2=quý)
            page: Trang (mặc định 1)
            page_size: Số kỳ trên mỗi trang (mặc định 4)
            show_log: Hiển thị log debug.
        """
        url = f"{_SAS_FINANCE_INFO_URL}/{self.symbol}"

        # Build params based on report type
        # Note: API is case-sensitive and requires specific parameters per report type
        params = {
            "page": page,
            "pageSize": page_size,
            "type": report_type,
            "unit": 1000,  # Đơn vị ngàn đồng
            "termtype": period_type,  # 1=năm, 2=quý (lowercase!)
        }

        # Add languageid for most report types (except cash flow which uses termType)
        if report_type != "LCTT":
            params["languageid"] = 1
        else:
            # Cash flow uses different parameter names
            params["code"] = self.symbol
            params["termType"] = period_type  # Cash flow uses camelCase termType

        # Log request configuration using logger
        if show_log or self.show_log:
            logger.info(
                f"KBS Financial API Request: {self.symbol} - {report_type} - Period: {period_type}"
            )

        try:
            json_data = send_request(
                url=url,
                headers=self.headers,
                method="GET",
                params=params,
                show_log=show_log or self.show_log,
                proxy_list=self.proxy_config.proxy_list,
                proxy_mode=self.proxy_config.proxy_mode,
                request_mode=self.proxy_config.request_mode,
            )

            if show_log or self.show_log:
                if isinstance(json_data, dict) and "data" in json_data:
                    logger.info(
                        f"API Response received: {len(json_data.get('data', []))} records"
                    )

            return json_data
        except Exception as e:
            if show_log or self.show_log:
                logger.error(f"API Request Failed: {str(e)}")
            raise

    @optimize_execution("KBS")
    def income_statement(
        self,
        period: Optional[str] = None,
        include_metadata: bool = False,
        display_mode: Optional[Union[str, FieldDisplayMode]] = FieldDisplayMode.STD,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Truy xuất báo cáo kết quả kinh doanh (income statement).

        Args:
            period: Loại kỳ báo cáo ('year' hoặc 'quarter'). Mặc định 'year'.
            include_metadata: Bao gồm thông tin audit và unit trong rows. Mặc định False.
            display_mode: Chế độ hiển thị trường dữ liệu. Mặc định FieldDisplayMode.STD.
                - FieldDisplayMode.STD: Chỉ giữ cột 'item' và 'item_id' (đã chuẩn hóa)
                - FieldDisplayMode.ALL: Giữ tất cả cột item (item, item_en, item_id)
                - 'vi': Chỉ giữ tên tiếng Việt (tương thích ngược)
                - 'en': Chỉ giữ tên tiếng Anh (tương thích ngược)
                - None: Giữ tất cả cột (tương thích ngược)
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa báo cáo kết quả kinh doanh.
        """
        # Map period to termType (1=year, 2=quarter)
        effective_period = (
            period if period else (self.period if self.period else "year")
        )
        period_type = 1 if effective_period == "year" else 2

        # Fetch data with pagination support
        df = self._fetch_series_data(
            report_type="KQKD",
            period_type=period_type,
            report_key="Kết quả kinh doanh",
            include_metadata=include_metadata,
            show_log=show_log,
        )

        if df.empty:
            logger.warning(
                f"Không tìm thấy báo cáo kết quả kinh doanh cho {self.symbol}."
            )
            return pd.DataFrame()

        # Apply schema standardization if enabled
        if self.standardize_columns:
            df = self._apply_schema_standardization(df, "income_statement")

        # Filter columns by display mode
        df = self._filter_columns_by_lang(df, display_mode)

        # Add metadata
        df.attrs["symbol"] = self.symbol
        df.attrs["source"] = self.data_source
        df.attrs["report_type"] = "income_statement"
        df.attrs["period"] = period

        if show_log or self.show_log:
            logger.info(
                f"Truy xuất thành công báo cáo kết quả kinh doanh cho {self.symbol}."
            )

        return df

    @optimize_execution("KBS")
    def balance_sheet(
        self,
        period: Optional[str] = None,
        include_metadata: bool = False,
        display_mode: Optional[Union[str, FieldDisplayMode]] = FieldDisplayMode.STD,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Truy xuất bảng cân đối kế toán (balance sheet).

        Args:
            period: Loại kỳ báo cáo ('year' hoặc 'quarter'). Mặc định 'year'.
            include_metadata: Bao gồm thông tin audit và unit trong rows. Mặc định False.
            display_mode: Chế độ hiển thị trường dữ liệu. Mặc định FieldDisplayMode.STD.
                - FieldDisplayMode.STD: Chỉ giữ cột 'item' và 'item_id' (đã chuẩn hóa)
                - FieldDisplayMode.ALL: Giữ tất cả cột item (item, item_en, item_id)
                - 'vi': Chỉ giữ tên tiếng Việt (tương thích ngược)
                - 'en': Chỉ giữ tên tiếng Anh (tương thích ngược)
                - None: Giữ tất cả cột (tương thích ngược)
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa bảng cân đối kế toán.
        """
        # Map period to termType (1=year, 2=quarter)
        effective_period = (
            period if period else (self.period if self.period else "year")
        )
        period_type = 1 if effective_period == "year" else 2

        # Fetch data with pagination support
        df = self._fetch_series_data(
            report_type="CDKT",
            period_type=period_type,
            report_key="Cân đối kế toán",
            include_metadata=include_metadata,
            show_log=show_log,
        )

        if df.empty:
            logger.warning(f"Không tìm thấy bảng cân đối kế toán cho {self.symbol}.")
            return pd.DataFrame()

        # Apply schema standardization if enabled
        if self.standardize_columns:
            df = self._apply_schema_standardization(df, "balance_sheet")

        # Filter columns by display mode
        df = self._filter_columns_by_lang(df, display_mode)

        # Add metadata
        df.attrs["symbol"] = self.symbol
        df.attrs["source"] = self.data_source
        df.attrs["report_type"] = "balance_sheet"
        df.attrs["period"] = period

        if show_log or self.show_log:
            logger.info(f"Truy xuất thành công bảng cân đối kế toán cho {self.symbol}.")

        return df

    @optimize_execution("KBS")
    def cash_flow(
        self,
        period: Optional[str] = None,
        include_metadata: bool = False,
        display_mode: Optional[Union[str, FieldDisplayMode]] = FieldDisplayMode.STD,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Truy xuất báo cáo lưu chuyển tiền tệ (cash flow statement).

        Args:
            period: Loại kỳ báo cáo ('year' hoặc 'quarter'). Mặc định 'year'.
            include_metadata: Bao gồm thông tin audit và unit trong rows. Mặc định False.
            display_mode: Chế độ hiển thị trường dữ liệu. Mặc định FieldDisplayMode.STD.
                - FieldDisplayMode.STD: Chỉ giữ cột 'item' và 'item_id' (đã chuẩn hóa)
                - FieldDisplayMode.ALL: Giữ tất cả cột item (item, item_en, item_id)
                - 'vi': Chỉ giữ tên tiếng Việt (tương thích ngược)
                - 'en': Chỉ giữ tên tiếng Anh (tương thích ngược)
                - None: Giữ tất cả cột (tương thích ngược)
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa báo cáo lưu chuyển tiền tệ.
        """
        # Map period to termType (1=year, 2=quarter)
        effective_period = (
            period if period else (self.period if self.period else "year")
        )
        period_type = 1 if effective_period == "year" else 2

        # Fetch one record to determine which cash flow key exists for this company
        probe_data = self._fetch_financial_data(
            report_type="LCTT", period_type=period_type, page_size=1, show_log=False
        )
        if not probe_data:
            raise ValueError(f"Không tìm thấy dữ liệu tài chính cho mã {self.symbol}.")

        content = probe_data.get("Content", {})
        cash_flow_key = None
        if "Lưu chuyển tiền tệ gián tiếp" in content:
            cash_flow_key = "Lưu chuyển tiền tệ gián tiếp"
        elif "Lưu chuyển tiền tệ trực tiếp" in content:
            cash_flow_key = "Lưu chuyển tiền tệ trực tiếp"

        if not cash_flow_key:
            logger.warning(
                f"Không tìm thấy báo cáo lưu chuyển tiền tệ cho {self.symbol}."
            )
            return pd.DataFrame()

        # Fetch with pagination support
        df = self._fetch_series_data(
            report_type="LCTT",
            period_type=period_type,
            report_key=cash_flow_key,
            include_metadata=include_metadata,
            show_log=show_log,
        )

        if df.empty:
            logger.warning(
                f"Không tìm thấy báo cáo lưu chuyển tiền tệ cho {self.symbol}."
            )
            return pd.DataFrame()

        # Apply schema standardization if enabled
        if self.standardize_columns:
            df = self._apply_schema_standardization(df, "cash_flow")

        # Filter columns by display mode
        df = self._filter_columns_by_lang(df, display_mode)

        # Add metadata
        df.attrs["symbol"] = self.symbol
        df.attrs["source"] = self.data_source
        df.attrs["report_type"] = "cash_flow"
        df.attrs["period"] = period

        if show_log or self.show_log:
            logger.info(
                f"Truy xuất thành công báo cáo lưu chuyển tiền tệ cho {self.symbol}."
            )

        return df

    @optimize_execution("KBS")
    def ratio(
        self,
        period: Optional[str] = None,
        include_metadata: bool = False,
        display_mode: Optional[Union[str, FieldDisplayMode]] = FieldDisplayMode.STD,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Truy xuất các chỉ số tài chính (financial ratios).

        Args:
            period: Loại kỳ báo cáo ('year' hoặc 'quarter'). Mặc định 'year'.
            include_metadata: Bao gồm thông tin audit và unit trong rows. Mặc định False.
            display_mode: Chế độ hiển thị trường dữ liệu. Mặc định FieldDisplayMode.STD.
                - FieldDisplayMode.STD: Chỉ giữ cột 'item' và 'item_id' (đã chuẩn hóa)
                - FieldDisplayMode.ALL: Giữ tất cả cột item (item, item_en, item_id)
                - 'vi': Chỉ giữ tên tiếng Việt (tương thích ngược)
                - 'en': Chỉ giữ tên tiếng Anh (tương thích ngược)
                - None: Giữ tất cả cột (tương thích ngược)
            show_log: Hiển thị log debug.

        Returns:
            DataFrame chứa các chỉ số tài chính.
        """
        # Map period to termType (1=year, 2=quarter)
        effective_period = (
            period if period else (self.period if self.period else "year")
        )
        period_type = 1 if effective_period == "year" else 2

        # Fetch data up to limit
        effective_limit = getattr(self, "limit", 4)
        dfs = []
        collected_periods = set()
        page = 1
        request_page_size = max(effective_limit, 4)

        while len(collected_periods) < effective_limit:
            financial_data = self._fetch_financial_data(
                report_type="CSTC",
                period_type=period_type,
                page=page,
                page_size=request_page_size,
                show_log=show_log,
            )

            if not financial_data:
                break

            content = financial_data.get("Content", {})
            ratio_groups = [k for k in content.keys() if "Nhóm chỉ số" in k]

            if not ratio_groups:
                break

            # Collect all ratio data from all groups
            all_ratio_data = []
            for group_key in ratio_groups:
                group_data = content.get(group_key, [])
                if group_data:
                    all_ratio_data.extend(group_data)

            if not all_ratio_data:
                break

            # Inject 'Financial Ratios Combined' into content and use _parse_financial_response
            financial_data["Content"]["Financial Ratios Combined"] = all_ratio_data

            df = self._parse_financial_response(
                financial_data,
                "Financial Ratios Combined",
                include_metadata=include_metadata,
            )

            if df.empty:
                break

            new_periods = df.attrs.get("periods", [])
            if not new_periods:
                break

            # Filter out periods we already have
            actual_new_periods = [p for p in new_periods if p not in collected_periods]
            if not actual_new_periods:
                break

            # If some periods are repeats, we only keep the new ones in this DF
            if len(actual_new_periods) < len(new_periods):
                cols_to_keep = [
                    c
                    for c in df.columns
                    if c not in new_periods or c in actual_new_periods
                ]
                df = df[cols_to_keep]
                df.attrs["periods"] = actual_new_periods

            dfs.append(df)
            collected_periods.update(actual_new_periods)

            page += 1
            if page > 20:
                break

        if not dfs:
            logger.warning(f"Không tìm thấy chỉ số tài chính cho {self.symbol}.")
            return pd.DataFrame()

        # Merge DataFrames on item_id
        final_df = dfs[0]

        for i in range(1, len(dfs)):
            next_df = dfs[i]
            next_periods = next_df.attrs.get("periods", [])

            cols_to_merge = ["item_id"] + next_periods

            if "item_id" in next_df.columns:
                current_attrs = final_df.attrs
                final_df = pd.merge(
                    final_df, next_df[cols_to_merge], on="item_id", how="outer"
                )
                current_attrs["periods"].extend(next_periods)
                if "audit_status" in next_df.attrs:
                    current_attrs["audit_status"].update(next_df.attrs["audit_status"])
                if "unit_type" in next_df.attrs:
                    current_attrs["unit_type"].update(next_df.attrs["unit_type"])
                final_df.attrs = current_attrs

        df = final_df

        # Truncate to limit
        all_periods = df.attrs.get("periods", [])
        if len(all_periods) > effective_limit:
            kept_periods = all_periods[:effective_limit]
            drop_periods = [p for p in all_periods if p not in kept_periods]
            df = df.drop(columns=drop_periods, errors="ignore")
            df.attrs["periods"] = kept_periods

        # Capture periods from first group
        df.attrs["report_key"] = "Financial Ratios"

        if df.empty:
            logger.warning(f"Không tìm thấy chỉ số tài chính cho {self.symbol}.")
            return pd.DataFrame()

        # Apply schema standardization if enabled
        if self.standardize_columns:
            df = self._apply_schema_standardization(df, "financial_ratios")

        # Filter columns by display mode
        df = self._filter_columns_by_lang(df, display_mode)

        # Add metadata
        df.attrs["symbol"] = self.symbol
        df.attrs["source"] = self.data_source
        df.attrs["report_type"] = "financial_ratios"
        df.attrs["period"] = period

        if show_log or self.show_log:
            logger.info(f"Truy xuất thành công chỉ số tài chính cho {self.symbol}.")

        return df


# Register KBS Financial provider
from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401

ProviderRegistry.register("financial", "kbs", Finance)
