"""Company module for KB Securities (KBS) data source."""

from typing import Dict, Optional

import pandas as pd
from vnai import optimize_execution

from vnstock.core.utils.client import send_request
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.parser import camel_to_snake, get_asset_type
from vnstock.core.utils.transform import clean_html_dict
from vnstock.core.utils.user_agent import get_headers
from vnstock.explorer.kbs.const import (
    _CHARTER_CAPITAL_MAP,
    _COMPANY_PROFILE_MAP,
    _EVENT_TYPE,
    _EXCHANGE_CODE_MAP,
    _LABOR_STRUCTURE_MAP,
    _LEADERS_MAP,
    _OWNERSHIP_MAP,
    _SHAREHOLDERS_MAP,
    _STOCK_INFO_URL,
    _SUBSIDIARIES_MAP,
)

logger = get_logger(__name__)


class Company:
    """
    Access company information published by KB Securities (KBS).

    The source returns every section in one payload, so this class fetches it once,
    caches it, and shapes the slice each method needs from that cache. Same structure
    as the VCI Company class.
    """  # noqa: W293

    def __init__(
        self,
        symbol: str = None,
        random_agent: Optional[bool] = False,
        show_log: Optional[bool] = False,
    ):
        """
        Initialise the KBS Company client.

        Args:
            symbol: Ticker symbol, e.g. 'ACB' or 'VNM'.
            random_agent: Deprecated and ignored. Defaults to False.
            show_log: Show debug logs. Defaults to False.

        Raises:
            ValueError: If the symbol is not a stock.
        """
        self.symbol = symbol.upper() if symbol else ""
        self.asset_type = get_asset_type(self.symbol) if symbol else "stock"

        # Validate if symbol is a stock
        if symbol and self.asset_type not in ["stock"]:
            raise ValueError("Mã CK không hợp lệ hoặc không phải cổ phiếu.")

        self.data_source = "KBS"
        self.headers = get_headers(
            data_source=self.data_source, random_agent=random_agent
        )
        self.show_log = show_log

        if not show_log:
            logger.setLevel("CRITICAL")

        # Cache for raw data (fetch once, use multiple times)
        self._raw_data = None
        self._cache_loaded = False

    def _load_cache(self, show_log: Optional[bool] = False) -> Dict:
        """
        Fetch the company payload once and cache it.

        Returns:
            Dictionary holding every company section.
        """  # noqa: W293
        if self._cache_loaded and self._raw_data is not None:
            return self._raw_data

        url = f"{_STOCK_INFO_URL}/profile/{self.symbol}"
        params = {"l": 1}  # Language param (1 for Vietnamese)

        json_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            params=params,
            show_log=show_log or self.show_log,
        )

        self._raw_data = json_data
        self._cache_loaded = True
        return json_data

    def _fetch_profile(self, show_log: Optional[bool] = False) -> Dict:
        """
        Read the company profile from the cache, fetching it if needed.

        Args:
            show_log: Show debug logs.

        Returns:
            Dictionary holding the company profile.
        """
        return self._load_cache(show_log=show_log)

    def _process_profile_data(self, raw_data: Dict) -> pd.DataFrame:
        """
        Shape the raw profile payload.

        Args:
            raw_data: Raw payload from the API

        Returns:
            DataFrame with the standardised profile
        """  # noqa: W293
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
        if "LaborStructure" in raw_data and raw_data["LaborStructure"]:
            labor_data = raw_data["LaborStructure"]
            if isinstance(labor_data, list) and len(labor_data) > 0:
                # Sum up all employee counts from labor structure
                total_employees = sum(
                    int(item.get("Value", 0))
                    for item in labor_data
                    if isinstance(item.get("Value"), (int, str))
                )
                if total_employees > 0:
                    profile_dict["number_of_employees"] = total_employees

        # Convert to DataFrame
        df = pd.DataFrame([profile_dict])

        # Normalize exchange code
        if "exchange" in df.columns:
            df["exchange"] = df["exchange"].map(
                lambda x: _EXCHANGE_CODE_MAP.get(x, x) if pd.notna(x) else x
            )

        # Add metadata
        df.attrs["symbol"] = self.symbol
        df.attrs["source"] = self.data_source

        return df

    def _process_subsidiaries(self, raw_data: Dict) -> pd.DataFrame:
        """
        Shape the raw subsidiaries payload.

        Args:
            raw_data: Raw payload from the API

        Returns:
            DataFrame of subsidiaries
        """  # noqa: W293
        if "Subsidiaries" not in raw_data or not raw_data["Subsidiaries"]:
            return pd.DataFrame()

        # Convert list to DataFrame
        df = pd.DataFrame(raw_data["Subsidiaries"])

        # Rename columns
        df = df.rename(columns=_SUBSIDIARIES_MAP)

        # Convert date columns
        for col in ["date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        # Add metadata
        df.attrs["symbol"] = self.symbol
        df.attrs["source"] = self.data_source

        return df

    def _process_leaders(self, raw_data: Dict) -> pd.DataFrame:
        """
        Shape the raw management payload.

        Args:
            raw_data: Raw payload from the API

        Returns:
            DataFrame of company officers
        """  # noqa: W293
        if "Leaders" not in raw_data or not raw_data["Leaders"]:
            return pd.DataFrame()

        # Convert list to DataFrame
        df = pd.DataFrame(raw_data["Leaders"])

        # Rename columns
        df = df.rename(columns=_LEADERS_MAP)

        # Add metadata
        df.attrs["symbol"] = self.symbol
        df.attrs["source"] = self.data_source

        return df

    def _process_ownership(self, raw_data: Dict) -> pd.DataFrame:
        """
        Shape the raw ownership payload.

        Args:
            raw_data: Raw payload from the API

        Returns:
            DataFrame of the ownership breakdown
        """  # noqa: W293
        if "Ownership" not in raw_data or not raw_data["Ownership"]:
            return pd.DataFrame()

        # Convert list to DataFrame
        df = pd.DataFrame(raw_data["Ownership"])

        # Rename columns
        df = df.rename(columns=_OWNERSHIP_MAP)

        # Convert date columns
        for col in ["date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        # Add metadata
        df.attrs["symbol"] = self.symbol
        df.attrs["source"] = self.data_source

        return df

    def _process_shareholders(self, raw_data: Dict) -> pd.DataFrame:
        """
        Shape the raw major-shareholder payload.

        Args:
            raw_data: Raw payload from the API

        Returns:
            DataFrame of major shareholders
        """  # noqa: W293
        if "Shareholders" not in raw_data or not raw_data["Shareholders"]:
            return pd.DataFrame()

        # Convert list to DataFrame
        df = pd.DataFrame(raw_data["Shareholders"])

        # Rename columns
        df = df.rename(columns=_SHAREHOLDERS_MAP)

        # Convert date columns
        for col in ["date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        # Add metadata
        df.attrs["symbol"] = self.symbol
        df.attrs["source"] = self.data_source

        return df

    def _process_charter_capital(self, raw_data: Dict) -> pd.DataFrame:
        """
        Shape the raw charter-capital history payload.

        Args:
            raw_data: Raw payload from the API

        Returns:
            DataFrame of charter capital over time
        """  # noqa: W293
        if "CharterCapital" not in raw_data or not raw_data["CharterCapital"]:
            return pd.DataFrame()

        # Convert list to DataFrame
        df = pd.DataFrame(raw_data["CharterCapital"])

        # Rename columns
        df = df.rename(columns=_CHARTER_CAPITAL_MAP)

        # Convert date columns
        for col in ["date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        # Add metadata
        df.attrs["symbol"] = self.symbol
        df.attrs["source"] = self.data_source

        return df

    def _process_labor_structure(self, raw_data: Dict) -> pd.DataFrame:
        """
        Shape the raw workforce payload.

        Args:
            raw_data: Raw payload from the API

        Returns:
            DataFrame of the workforce breakdown
        """  # noqa: W293
        if "LaborStructure" not in raw_data or not raw_data["LaborStructure"]:
            return pd.DataFrame()

        # Convert list to DataFrame
        df = pd.DataFrame(raw_data["LaborStructure"])

        # Rename columns
        df = df.rename(columns=_LABOR_STRUCTURE_MAP)

        # Add metadata
        df.attrs["symbol"] = self.symbol
        df.attrs["source"] = self.data_source

        return df

    @optimize_execution("KBS")
    def overview(self, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Retrieve the company overview.

        Args:
            show_log: Show debug logs.

        Returns:
            DataFrame with the company overview.

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
            logger.info(f"Truy xuất thành công thông tin tổng quan cho {self.symbol}.")

        return df

    @optimize_execution("KBS")
    def officers(self, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Retrieve the company officers.

        Args:
            show_log: Show debug logs.

        Returns:
            DataFrame of company officers.

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
            logger.info(
                f"Truy xuất thành công {len(df)} lãnh đạo công ty cho {self.symbol}."
            )

        return df

    @optimize_execution("KBS")
    def shareholders(self, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Retrieve the company shareholders.

        Args:
            show_log: Show debug logs.

        Returns:
            DataFrame of shareholders.

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
            logger.info(f"Truy xuất thành công {len(df)} cổ đông cho {self.symbol}.")

        return df

    @optimize_execution("KBS")
    def ownership(self, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Retrieve the ownership breakdown.

        Args:
            show_log: Show debug logs.

        Returns:
            DataFrame of the ownership breakdown.

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
            logger.info(f"Truy xuất thành công cơ cấu cổ đông cho {self.symbol}.")

        return df

    @optimize_execution("KBS")
    def subsidiaries(self, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Retrieve subsidiaries and affiliates.

        Covers both subsidiaries (ownership above 50%) and affiliates (50% or less);
        the 'type' column tells them apart.

        Args:
            show_log: Show debug logs.

        Returns:
            DataFrame of subsidiaries and affiliates.

        Examples:
            >>> company = Company('ACB')
            >>> df = company.subsidiaries()
            >>> print(df.columns.tolist())
            ['date', 'name', 'charter_capital', 'ownership_ratio', 'currency', 'type']
        """  # noqa: W293
        profile_data = self._fetch_profile(show_log=show_log)

        if not profile_data:
            return pd.DataFrame()

        df = self._process_subsidiaries(profile_data)

        if len(df) > 0:
            # Add type column to distinguish subsidiaries and affiliates
            df["type"] = df["ownership_percent"].apply(
                lambda x: "công ty con" if x > 50 else "công ty liên kết"
            )

        if show_log or self.show_log:
            logger.info(
                f"Truy xuất thành công {len(df)} công ty con/liên kết cho {self.symbol}."
            )

        return df

    @optimize_execution("KBS")
    def affiliate(self, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Retrieve affiliates, meaning holdings of 50% or less.

        Filtered out of the subsidiaries list.

        Args:
            show_log: Show debug logs.

        Returns:
            DataFrame of affiliates.
        """  # noqa: W293
        profile_data = self._fetch_profile(show_log=show_log)

        if not profile_data:
            return pd.DataFrame()

        df = self._process_subsidiaries(profile_data)

        if len(df) == 0:
            return df

        # Filter affiliates: ownership_percent <= 50%
        df_affiliate = df[df["ownership_percent"] <= 50].copy()
        df_affiliate["type"] = "công ty liên kết"

        if show_log or self.show_log:
            logger.info(
                f"Truy xuất thành công {len(df_affiliate)} công ty liên kết cho {self.symbol}."
            )

        return df_affiliate

    @optimize_execution("KBS")
    def capital_history(self, show_log: Optional[bool] = False) -> pd.DataFrame:
        """
        Retrieve the charter capital history.

        Args:
            show_log: Show debug logs.

        Returns:
            DataFrame of charter capital over time.

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
            logger.info(f"Truy xuất thành công lịch sử vốn điều lệ cho {self.symbol}.")

        return df

    @optimize_execution("KBS")
    def events(
        self,
        event_type: Optional[int] = None,
        page: int = 1,
        page_size: int = 10,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Retrieve the company events.

        Args:
            event_type: Event type, 1 to 5. None returns every type.
                        1 shareholder meeting, 2 dividend payment, 3 share issuance,
                        4 insider trading, 5 other.
            page: Page number. Defaults to 1.
            page_size: Records per page. Defaults to 10.
            show_log: Show debug logs.

        Returns:
            DataFrame of events.

        Examples:
            >>> company = Company('ACB')
            >>> df = company.events(event_type=2)  # dividend payments
        """  # noqa: W291
        url = f"{_STOCK_INFO_URL}/event/{self.symbol}"

        # Build params
        params = {
            "l": 1,  # Language
            "p": page,
            "s": page_size,
        }

        if event_type is not None:
            if event_type not in _EVENT_TYPE:
                raise ValueError(
                    f"event_type không hợp lệ. Các giá trị hợp lệ: {list(_EVENT_TYPE.keys())}"
                )
            params["eID"] = event_type

        json_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            params=params,
            show_log=show_log or self.show_log,
        )

        if not json_data:
            return pd.DataFrame()

        # Convert to DataFrame
        df = (
            pd.DataFrame([json_data])
            if isinstance(json_data, dict)
            else pd.DataFrame(json_data)
        )

        # Convert column names to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]

        # Add metadata
        df.attrs["symbol"] = self.symbol
        df.attrs["source"] = self.data_source
        if event_type:
            df.attrs["event_type"] = _EVENT_TYPE[event_type]

        if show_log or self.show_log:
            logger.info(f"Truy xuất thành công {len(df)} sự kiện cho {self.symbol}.")

        return df

    @optimize_execution("KBS")
    def news(
        self,
        page: int = 1,
        page_size: int = 10,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Retrieve news about the company.

        Args:
            page: Page number. Defaults to 1.
            page_size: Records per page. Defaults to 10.
            show_log: Show debug logs.

        Returns:
            DataFrame of news items.

        Examples:
            >>> company = Company('ACB')
            >>> df = company.news(page=1, page_size=20)
        """
        url = f"{_STOCK_INFO_URL}/news/{self.symbol}"

        params = {
            "l": 1,  # Language
            "p": page,
            "s": page_size,
        }

        json_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            params=params,
            show_log=show_log or self.show_log,
        )

        if not json_data:
            return pd.DataFrame()

        # Convert to DataFrame
        df = (
            pd.DataFrame([json_data])
            if isinstance(json_data, dict)
            else pd.DataFrame(json_data)
        )

        # Convert column names to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]

        # Add metadata
        df.attrs["symbol"] = self.symbol
        df.attrs["source"] = self.data_source

        if show_log or self.show_log:
            logger.info(f"Truy xuất thành công {len(df)} tin tức cho {self.symbol}.")

        return df

    @optimize_execution("KBS")
    def insider_trading(
        self,
        page: int = 1,
        page_size: int = 10,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Retrieve insider trading records.

        Args:
            page: Page number. Defaults to 1.
            page_size: Records per page. Defaults to 10.
            show_log: Show debug logs.

        Returns:
            DataFrame of insider trades.

        Examples:
            >>> company = Company('ACB')
            >>> df = company.insider_trading()
        """
        url = f"{_STOCK_INFO_URL}/news/internal-trading/{self.symbol}"

        params = {
            "l": 1,  # Language
            "p": page,
            "s": page_size,
        }

        json_data = send_request(
            url=url,
            headers=self.headers,
            method="GET",
            params=params,
            show_log=show_log or self.show_log,
        )

        if not json_data:
            return pd.DataFrame()

        # Convert to DataFrame
        df = (
            pd.DataFrame([json_data])
            if isinstance(json_data, dict)
            else pd.DataFrame(json_data)
        )

        # Convert column names to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]

        # Add metadata
        df.attrs["symbol"] = self.symbol
        df.attrs["source"] = self.data_source

        if show_log or self.show_log:
            logger.info(
                f"Truy xuất thành công {len(df)} bản ghi giao dịch nội bộ cho {self.symbol}."
            )

        return df


# Register KBS Company provider
from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401

ProviderRegistry.register("company", "kbs", Company)
