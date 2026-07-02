"""Trading module for DNSE (Entrade) data source."""

from typing import List, Optional

import pandas as pd
from vnai import optimize_execution

from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401
from vnstock.core.utils.client import ProxyConfig, send_request
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers
from vnstock.explorer.dnse.const import (
    _PRICE_BOARD_MAP,
    _PRICE_BOARD_STANDARD_COLUMNS,
    _PRICE_BOARD_URL,
)

logger = get_logger(__name__)


class Trading:
    """
    Lớp truy cập dữ liệu giao dịch từ DNSE (Entrade).
    """

    def __init__(
        self,
        symbol: Optional[str] = None,
        random_agent: Optional[bool] = False,
        proxy_config: Optional[ProxyConfig] = None,
        show_log: Optional[bool] = False,
        proxy_mode: Optional[str] = None,
        proxy_list: Optional[List[str]] = None,
    ):
        """
        Khởi tạo Trading client cho DNSE.

        Args:
            symbol: Mã chứng khoán (VD: 'ACB'). Optional cho market-wide queries.
            random_agent: Sử dụng user agent ngẫu nhiên. Mặc định False.
            proxy_config: Cấu hình proxy. Mặc định None.
            show_log: Hiển thị log debug. Mặc định False.
            proxy_mode: Chế độ proxy. Mặc định None.
            proxy_list: Danh sách proxy URLs. Mặc định None.
        """
        self.symbol = symbol.upper() if symbol else None
        self.data_source = "DNSE"
        self.headers = get_headers(
            data_source=self.data_source, random_agent=random_agent
        )
        self.show_log = show_log

        if proxy_config is None:
            p_mode = proxy_mode if proxy_mode else "try"
            req_mode = "proxy" if proxy_list and len(proxy_list) > 0 else "direct"
            self.proxy_config = ProxyConfig(
                proxy_mode=p_mode, proxy_list=proxy_list, request_mode=req_mode
            )
        else:
            self.proxy_config = proxy_config

        if not show_log:
            logger.setLevel("CRITICAL")

    @optimize_execution("DNSE")
    def price_board(
        self,
        symbols_list: List[str],
        show_log: Optional[bool] = False,
        get_all: bool = False,
    ) -> pd.DataFrame:
        """
        Truy xuất bảng giá realtime cho danh sách mã chứng khoán từ DNSE.

        Args:
            symbols_list: Danh sách mã chứng khoán (VD: ['ACB', 'VNM']).
            show_log: Hiển thị log debug. Mặc định False.
            get_all: Giữ tất cả cột từ API response. Mặc định False.

        Returns:
            DataFrame với thông tin bảng giá cho các mã chứng khoán.

        Raises:
            ValueError: Nếu symbols_list rỗng.
        """
        if not symbols_list:
            raise ValueError("symbols_list không được để trống.")

        symbols_list = [s.upper() for s in symbols_list]
        symbols_param = ",".join(symbols_list)

        params = {"symbols": symbols_param}

        json_data = send_request(
            url=_PRICE_BOARD_URL,
            headers=self.headers,
            method="GET",
            params=params,
            show_log=show_log or self.show_log,
            proxy_list=self.proxy_config.proxy_list,
            proxy_mode=self.proxy_config.proxy_mode,
            request_mode=self.proxy_config.request_mode,
        )

        if not json_data:
            df = pd.DataFrame()
            df.attrs["symbols"] = symbols_list
            df.attrs["source"] = self.data_source
            return df

        # json_data may be a dict with "data" key, or a list of dicts
        if isinstance(json_data, dict) and "data" in json_data:
            records = json_data["data"]
        elif isinstance(json_data, list):
            records = json_data
        else:
            records = []

        df = pd.DataFrame(records) if records else pd.DataFrame()

        if not df.empty:
            # Apply column mapping
            df = df.rename(columns=_PRICE_BOARD_MAP)

            if not get_all:
                available_cols = [
                    c for c in _PRICE_BOARD_STANDARD_COLUMNS if c in df.columns
                ]
                df = df[available_cols]

        # Metadata
        df.attrs["symbols"] = symbols_list
        df.attrs["source"] = self.data_source
        df.attrs["get_all"] = get_all

        if show_log or self.show_log:
            logger.info(
                f"Truy xuất thành công bảng giá DNSE cho {len(symbols_list)} mã chứng khoán."
            )

        return df


# Register DNSE Trading provider
ProviderRegistry.register("trading", "dnse", Trading)
