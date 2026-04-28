"""Trading module for KB Securities (KBS) data source."""

import pandas as pd
import json
import re
from datetime import datetime
from typing import Optional, List
from vnai import optimize_execution
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.parser import get_asset_type
from vnstock.core.utils.client import ProxyConfig
from vnstock.core.utils.user_agent import get_headers
from vnstock.explorer.kbs.const import (
    _IIS_BASE_URL,
    _STOCK_ISS_URL,
    _PRICE_BOARD_MAP,
    _PRICE_BOARD_STANDARD_COLUMNS,
    _EXCLUDED_COLUMNS, _EXCHANGE_CODE_MAP
)

logger = get_logger(__name__)


class Trading:
    """
    Lớp truy cập dữ liệu giao dịch từ KB Securities (KBS).
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
        Khởi tạo Trading client cho KBS.

        Args:
            symbol: Mã chứng khoán (VD: 'ACB', 'VNM'). Optional cho market-wide queries.
            random_agent: Sử dụng user agent ngẫu nhiên. Mặc định False.
            proxy_config: Cấu hình proxy. Mặc định None.
            show_log: Hiển thị log debug. Mặc định False.
            proxy_mode: Chế độ proxy (try, rotate, random, single). Mặc định None.
            proxy_list: Danh sách proxy URLs. Mặc định None.
        """
        self.symbol = symbol.upper() if symbol else None
        self.data_source = 'KBS'
        self.base_url = _IIS_BASE_URL
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

        if self.symbol:
            from vnstock.core.utils.parser import get_asset_type, convert_derivative_symbol
            self.asset_type = get_asset_type(self.symbol)
            
            # Auto-convert derivative symbols to new KRX format
            if self.asset_type == 'derivative':
                try:
                    new_symbol = convert_derivative_symbol(self.symbol)
                    logger.info(f"Converted derivative symbol {self.symbol} to {new_symbol} (KRX format)")
                    self.symbol = new_symbol
                except Exception as e:
                    logger.debug(f"Symbol conversion skipped for {self.symbol}: {e}")

        if not show_log:
            logger.setLevel('CRITICAL')

    def _fetch_stock_board(
        self,
        symbols_list: List[str],
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Fetch stock board (lô chẵn) data from /stock/iss endpoint.
        """
        import requests
        
        url = _STOCK_ISS_URL
        payload = {'code': ','.join(symbols_list)}
        
        try:
            # Build headers for stock ISS endpoint
            headers_stock = self.headers.copy()
            headers_stock.update({
                'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json',
                'DNT': '1',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'x-lang': 'vi'
            })
            
            response = requests.post(
                url,
                headers=headers_stock,
                data=json.dumps(payload),
                timeout=30
            )
            if response.status_code in [200, 201]:
                json_data = response.json()
            else:
                return pd.DataFrame()
        except Exception as e:
            if show_log or self.show_log:
                logger.error(f"Failed to fetch stock board data: {str(e)}")
            return pd.DataFrame()
        
        if not json_data or not isinstance(json_data, list):
            # Try to see if it's in a 'data' field
            if isinstance(json_data, dict) and 'data' in json_data:
                json_data = json_data['data']
            else:
                return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(json_data)
        return df

    def _fetch_derivative_board(
        self,
        symbols_list: List[str],
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Fetch derivative board data from /derivative/iss endpoint.
        """
        import requests
        
        url = f"{_IIS_BASE_URL}/derivative/iss"
        payload = {'code': ','.join(symbols_list)}
        
        try:
            headers_der = self.headers.copy()
            headers_der.update({
                'Content-Type': 'application/json',
                'x-lang': 'vi'
            })
            
            response = requests.post(
                url,
                headers=headers_der,
                data=json.dumps(payload),
                timeout=30
            )
            if response.status_code in [200, 201]:
                json_data = response.json()
            else:
                return pd.DataFrame()
        except Exception as e:
            if show_log or self.show_log:
                logger.error(f"Failed to fetch derivative board data: {str(e)}")
            return pd.DataFrame()
        
        if not json_data or 'data' not in json_data:
            return pd.DataFrame()
            
        return pd.DataFrame(json_data['data'])


    @optimize_execution("KBS")
    def price_board(
        self,
        symbols_list: List[str],
        exchange: str = 'HOSE',
        show_log: Optional[bool] = False,
        get_all: bool = False,
    ) -> pd.DataFrame:
        """
        Truy xuất bảng giá realtime cho danh sách mã chứng khoán.
        """
        if not symbols_list:
            raise ValueError("symbols_list không được để trống.")

        # Normalize symbols to uppercase
        symbols_list = [s.upper() for s in symbols_list]
        
        # Determine if we should use derivative endpoint
        from vnstock.core.utils.parser import get_asset_type, convert_derivative_symbol
        
        # Convert symbols if needed
        converted_symbols = []
        is_derivative = False
        for s in symbols_list:
            atype = get_asset_type(s)
            if atype == 'derivative':
                is_derivative = True
                try:
                    cs = convert_derivative_symbol(s)
                    converted_symbols.append(cs)
                except Exception as e:
                    converted_symbols.append(s)
            else:
                converted_symbols.append(s)

        # Route to appropriate endpoint based on board type
        if is_derivative:
            df = self._fetch_derivative_board(converted_symbols, show_log)
            data_label = 'phái sinh'
        else:
            df = self._fetch_stock_board(converted_symbols, show_log)
            data_label = 'lô chẵn'
            
        standard_cols = _PRICE_BOARD_STANDARD_COLUMNS
        # Add open_interest to standard columns for derivatives
        if is_derivative:
            standard_cols = standard_cols + ['open_interest']

        # Filter columns based on get_all parameter
        if len(df) > 0:
            # Apply column mapping
            df = df.rename(columns=_PRICE_BOARD_MAP)
            
            if not get_all:
                # Keep only standard columns that exist in the dataframe
                available_cols = [col for col in standard_cols if col in df.columns]
                df = df[available_cols]
            else:
                # Remove unclear/meaningless columns from get_all output
                cols_to_keep = [col for col in df.columns if col not in _EXCLUDED_COLUMNS]
                df = df[cols_to_keep]
            
            # Normalize exchange codes
            if 'exchange' in df.columns:
                df['exchange'] = df['exchange'].map(
                    lambda x: _EXCHANGE_CODE_MAP.get(x, x) if pd.notna(x) else x
                )

        # Update metadata
        df.attrs['symbols'] = symbols_list
        df.attrs['source'] = self.data_source
        df.attrs['get_all'] = get_all

        if show_log or self.show_log:
            logger.info(
                f'Truy xuất thành công bảng giá {data_label} cho {len(symbols_list)} mã chứng khoán.'
            )

        return df


# Register KBS Trading provider
from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401
ProviderRegistry.register('trading', 'kbs', Trading)
