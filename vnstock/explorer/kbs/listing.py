"""Listing module for KB Securities (KBS) data source."""

from typing import Dict, List, Optional, Union
import json
import pandas as pd
from vnai import agg_execution
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.client import send_request, ProxyConfig
from vnstock.core.utils.user_agent import get_headers
from vnstock.explorer.kbs.const import (
    _IIS_BASE_URL, _SEARCH_URL, _SECTOR_ALL_URL, _SECTOR_STOCK_URL, _INDEX_URL, _GROUP_CODE, _INDUSTRY_CODE
)

logger = get_logger(__name__)


class Listing:
    """
    Lớp truy cập dữ liệu danh sách mã chứng khoán từ KB Securities (KBS).
    """

    def __init__(
        self,
        random_agent: Optional[bool] = False,
        proxy_config: Optional[ProxyConfig] = None,
        show_log: Optional[bool] = False,
        proxy_mode: Optional[str] = None,
        proxy_list: Optional[List[str]] = None,
    ):
        """
        Khởi tạo Listing client cho KBS.

        Args:
            random_agent: Sử dụng user agent ngẫu nhiên. Mặc định False.
            proxy_config: Cấu hình proxy. Mặc định None (không sử dụng proxy).
            show_log: Hiển thị log debug. Mặc định False.
            proxy_mode: Chế độ proxy (try, rotate, random, single). Mặc định None.
            proxy_list: Danh sách proxy URLs. Mặc định None.
        """
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
        
        if not show_log:
            logger.setLevel('CRITICAL')

    @agg_execution("KBS")
    def all_symbols(
        self,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Truy xuất danh sách toàn bộ mã chứng khoán trên thị trường Việt Nam từ KBS.

        Trả về DataFrame đơn giản với mapping symbol → organ_name (tên công ty tiếng Việt).

        Args:
            show_log: Hiển thị log debug. Mặc định False.

        Returns:
            DataFrame với 2 cột: symbol, organ_name.
            Metadata 'source' được lưu trong df.attrs['source'].

        Examples:
            >>> kbs = Listing()
            >>> df = kbs.all_symbols()
            >>> print(df.columns.tolist())
            ['symbol', 'organ_name']
            >>> print(df.attrs['source'])
            'KBS'
        """
        # Get full stock data from API
        try:
            stocks_data = self._get_full_stock_data(show_log=show_log)
        except Exception as e:
            if show_log:
                logger.error(f"Lỗi khi lấy dữ liệu chứng khoán: {str(e)}")
            return pd.DataFrame(columns=['symbol', 'organ_name'])
        
        if not stocks_data:
            return pd.DataFrame(columns=['symbol', 'organ_name'])
        
        # Convert to DataFrame
        df = pd.DataFrame(stocks_data).query("type == 'stock'")
        
        # Map 'name' to 'organ_name'
        if 'name' in df.columns:
            df = df.rename(columns={'name': 'organ_name'})
        
        # Keep only symbol, organ_name, and type columns
        df = df[['symbol', 'organ_name']]
        
        # Add source as attribute
        df.attrs['source'] = self.data_source
        
        if show_log:
            logger.info(f'Truy xuất thành công {len(df)} mã chứng khoán.')
        
        return df

    @agg_execution("KBS")
    def symbols_by_exchange(
        self,
        get_all: Optional[bool] = False,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Truy xuất danh sách mã chứng khoán theo sàn giao dịch.

        Sử dụng endpoint /stock/search/data để lấy dữ liệu đầy đủ.

        Args:
            get_all: Lấy tất cả các cột mà API cung cấp thay vì chỉ các cột chuẩn hoá. Mặc định False.
            show_log: Hiển thị log debug. Mặc định False.

        Returns:
            DataFrame chứa các cột từ API KBS: symbol, organ_name, en_organ_name,
            exchange, type, id, re, ceiling, floor.
            Metadata 'source' được lưu trong df.attrs['source'].
            Các cột không có sẽ bỏ qua.
        """
        # Get full stock data from API
        try:
            stocks_data = self._get_full_stock_data(show_log=show_log)
        except Exception as e:
            if show_log:
                logger.error(f"Lỗi khi lấy dữ liệu chứng khoán: {str(e)}")
            return pd.DataFrame(columns=['symbol', 'organ_name', 'exchange', 'source'])
        
        if not stocks_data:
            return pd.DataFrame(columns=['symbol', 'organ_name', 'exchange', 'source'])
        
        # Convert to DataFrame
        df = pd.DataFrame(stocks_data)
        
        # Map KBS columns to standard names (similar to VCI)
        column_mapping = {
            'name': 'organ_name',
            'nameEn': 'en_organ_name',
            'index': 'id',
        }
        df = df.rename(columns=column_mapping)
        
        # Define standard columns and filter by availability
        if get_all:
            standard_cols = ['symbol', 'organ_name', 'en_organ_name', 'exchange', 'type', 'id', 're', 'ceiling', 'floor']
            available_cols = [col for col in standard_cols if col in df.columns]
        else:
            available_cols = ['symbol', 'organ_name', 'en_organ_name', 'exchange', 'type', 'id']
        df = df[available_cols]
        df.attrs['source'] = self.data_source
        
        if show_log:
            logger.info(f'Truy xuất thành công {len(df)} mã chứng khoán theo sàn.')
        
        return df

    @agg_execution("KBS")
    def symbols_by_industries(
        self,
        lang: str = 'vi',
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Truy xuất danh sách mã chứng khoán theo nhóm ngành. Thông tin mã ngành là quy định riêng của KBS không theo chuẩn ICB thường gặp.

        Args:
            lang: Ngôn ngữ ('vi' hoặc 'en'). Mặc định 'vi'.
            show_log: Hiển thị log debug. Mặc định False.

        Returns:
            DataFrame chứa thông tin mã chứng khoán theo ngành.

        Raises:
            ValueError: Nếu ngôn ngữ không hợp lệ.
        """
        if lang not in ['vi', 'en']:
            raise ValueError("Ngôn ngữ phải là 'vi' hoặc 'en'.")

        # Get list of industries
        try:
            industries_data = self._get_industries_internal(show_log=show_log)
        except Exception as e:
            if show_log:
                logger.error(f"Lỗi khi lấy danh sách ngành: {str(e)}")
            # Return empty DataFrame if API fails
            df = pd.DataFrame(columns=['symbol', 'industry_code', 'industry_name'])
            df.attrs['source'] = self.data_source
            return df
        
        all_symbols_by_industry = []

        for industry in industries_data:
            code = industry['code']
            name = industry['name']
            
            try:
                symbols = self._get_symbols_by_industry_internal(
                    industry_code=code,
                    show_log=show_log
                )
                
                for symbol in symbols:
                    all_symbols_by_industry.append({
                        'symbol': symbol,
                        'industry_code': code,
                        'industry_name': name,
                    })
            except Exception as e:
                if show_log:
                    logger.warning(f"Lỗi khi lấy mã từ ngành {name} ({code}): {str(e)}")

        if all_symbols_by_industry:
            df = pd.DataFrame(all_symbols_by_industry)
            df.attrs['source'] = self.data_source
            return df
        else:
            df = pd.DataFrame(columns=['symbol', 'industry_code', 'industry_name'])
            df.attrs['source'] = self.data_source
            return df

    @agg_execution("KBS")
    def symbols_by_group(
        self,
        group: str = 'VN30',
        show_log: Optional[bool] = False,
    ) -> pd.Series:
        """
        Truy xuất danh sách mã chứng khoán theo nhóm chỉ số.

        Hỗ trợ lọc theo các nhóm/sàn: chỉ số VN (VN30, VN100, VNMidCap, VNSmallCap, VNSI, VNX50, VNXALL),
        sàn giao dịch (HOSE, HNX, UPCOM), chỉ số HNX30, ETF, chứng quyền (CW), trái phiếu (BOND),
        và phái sinh (DER).

        Để xem danh sách tất cả các nhóm được hỗ trợ, gọi `get_supported_groups()`.

        Args:
            group: Tên nhóm được hỗ trợ. Mặc định 'VN30'.
                   Ví dụ: 'VN30', 'VN100', 'HOSE', 'HNX', 'UPCOM', 'ETF', 'BOND', 'CW', 'FU_INDEX'.
            show_log: Hiển thị log debug. Mặc định False.

        Returns:
            Series chứa mã chứng khoán theo nhóm.

        Raises:
            ValueError: Nếu tên nhóm không hợp lệ.

        Example:
            >>> from quant_master.explorer.kbs import Listing
            >>> kbs = Listing()
            >>> # Lấy danh sách VN30
            >>> vn30 = kbs.symbols_by_group('VN30')
            >>> # Lấy tất cả ETF
            >>> etf_symbols = kbs.symbols_by_group('ETF')
            >>> # Xem tất cả nhóm được hỗ trợ
            >>> groups = kbs.get_supported_groups()
        """
        if group not in _GROUP_CODE:
            raise ValueError(f"Nhóm không hợp lệ. Sử dụng get_supported_groups() để xem danh sách nhóm được hỗ trợ.")

        symbols = self._get_symbols_by_group_internal(
            group=group,
            show_log=show_log
        )

        series = pd.Series(symbols, name='symbol')
        series.attrs['source'] = self.data_source
        series.attrs['group'] = group
        return series

    @agg_execution("KBS")
    def industries_icb(
        self,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        Truy xuất thông tin danh sách các ngành công nghiệp.

        Note: **KBS không cung cấp ICB classification.**
        
        Để lấy danh sách mã theo ngành, hãy sử dụng `symbols_by_industries()`.

        Raises:
            NotImplementedError: KBS không hỗ trợ ICB classification.
        """
        raise NotImplementedError(
            "KBS không cung cấp ICB classification. "
            "Sử dụng symbols_by_industries() để lấy mã theo ngành."
        )

    @agg_execution("KBS")
    def get_supported_groups(
        self,
    ) -> pd.DataFrame:
        """
        Liệt kê tất cả các nhóm/sàn được hỗ trợ bởi phương thức symbols_by_group().

        Các mô tả chỉ số tuân theo chuẩn của vnstock library.

        Returns:
            DataFrame với các cột:
            - group_name: Tên nhóm có thể truyền vào symbols_by_group()
            - group_code: Mã nội bộ của KBS
            - category: Danh mục (Chỉ số VN, Sàn giao dịch, ETF/Quỹ, Chứng quyền, Trái phiếu, Phái sinh)
            - description: Mô tả chi tiết theo chuẩn vnstock

        Example:
            >>> from quant_master.explorer.kbs import Listing
            >>> kbs = Listing()
            >>> groups = kbs.get_supported_groups()
            >>> print(groups)
            >>> # Lọc chỉ các chỉ số VN
            >>> vn_indices = groups[groups['category'] == 'Chỉ số VN']
        """
        group_info = {
            # Chỉ số VN - Mô tả theo chuẩn vnstock
            ('VN30', '30', 'Chỉ số VN', '30 cổ phiếu vốn hóa lớn nhất & thanh khoản tốt nhất HOSE'),
            ('VN100', '100', 'Chỉ số VN', '100 cổ phiếu có vốn hoá lớn nhất HOSE'),
            ('VNMidCap', 'MID', 'Chỉ số VN', 'Mid-Cap Index - nhóm cổ phiếu vốn hóa trung bình'),
            ('VNSmallCap', 'SML', 'Chỉ số VN', 'Small-Cap Index - nhóm cổ phiếu vốn hóa nhỏ'),
            ('VNSI', 'SI', 'Chỉ số VN', 'Vietnam Small-Cap Index'),
            ('VNX50', 'X50', 'Chỉ số VN', '50 cổ phiếu vốn hóa lớn nhất trên toàn bộ thị trường HOSE và HNX'),
            ('VNXALL', 'XALL', 'Chỉ số VN', 'Tất cả cổ phiếu trên toàn bộ thị trường HOSE và HNX'),
            ('VNALL', 'ALL', 'Chỉ số VN', 'Tất cả cổ phiếu trên HOSE và HNX'),
            ('HNX30', 'HNX30', 'Chỉ số VN', 'Chỉ số 30 cổ phiếu hàng đầu HNX'),
            # Sàn giao dịch
            ('HOSE', 'HOSE', 'Sàn giao dịch', 'Sở giao dịch chứng khoán TP. Hồ Chí Minh'),
            ('HNX', 'HNX', 'Sàn giao dịch', 'Sàn Giao dịch Chứng khoán Hà Nội'),
            ('UPCOM', 'UPCOM', 'Sàn giao dịch', 'Sàn Giao dịch OTC (UPCoM - Unlisted Public Company Market)'),
            # Quỹ và chứng chỉ
            ('ETF', 'FUND', 'ETF/Quỹ', 'Exchange-Traded Fund - Quỹ chỉ số và quỹ trao đổi'),
            # Chứng quyền
            ('CW', 'CW', 'Chứng quyền', 'Covered Warrant - Chứng quyền phát hành bởi các tổ chức tài chính'),
            # Trái phiếu
            ('BOND', 'BOND', 'Trái phiếu', 'Corporate Bond - Trái phiếu doanh nghiệp niêm yết'),
            # Phái sinh
            ('FU_INDEX', 'DER', 'Phái sinh', 'Futures - Hợp đồng tương lai chỉ số')
        }

        data = [
            {
                'group_name': name,
                'group_code': code,
                'category': category,
                'description': desc,
            }
            for name, code, category, desc in sorted(group_info)
        ]

        df = pd.DataFrame(data)
        df.attrs['source'] = self.data_source
        return df

    @agg_execution("KBS")
    def all_future_indices(
        self,
        show_log: Optional[bool] = False,
    ) -> pd.Series:
        """
        Truy xuất danh sách mã phái sinh hợp đồng tương lai.

        Args:
            show_log: Hiển thị log debug. Mặc định False.

        Returns:
            Series chứa mã phái sinh.
        """
        return self.symbols_by_group(group='FU_INDEX', show_log=show_log)

    @agg_execution("KBS")
    def all_covered_warrant(
        self,
        show_log: Optional[bool] = False,
    ) -> pd.Series:
        """
        Truy xuất danh sách mã chứng quyền.

        Args:
            show_log: Hiển thị log debug. Mặc định False.

        Returns:
            Series chứa mã chứng quyền.
        """
        return self.symbols_by_group(group='CW', show_log=show_log)

    @agg_execution("KBS")
    def all_bonds(
        self,
        show_log: Optional[bool] = False,
    ) -> pd.Series:
        """
        Truy xuất danh sách mã trái phiếu.

        Args:
            show_log: Hiển thị log debug. Mặc định False.

        Returns:
            Series chứa mã trái phiếu.
        """
        return self.symbols_by_group(group='BOND', show_log=show_log)

    @agg_execution("KBS")
    def all_etf(
        self,
        show_log: Optional[bool] = False,
    ) -> pd.Series:
        """
        Truy xuất danh sách mã quỹ ETF.

        Args:
            show_log: Hiển thị log debug. Mặc định False.

        Returns:
            Series chứa mã ETF.
        """
        return self.symbols_by_group(group='ETF', show_log=show_log)

    @agg_execution("KBS")
    def all_government_bonds(
        self,
        show_log: Optional[bool] = False,
    ) -> pd.Series:
        """
        Truy xuất danh sách mã trái phiếu chính phủ.

        Note: **KBS không cung cấp dữ liệu trái phiếu chính phủ.**

        Để lấy danh sách trái phiếu doanh nghiệp, hãy sử dụng `all_bonds()`.

        Raises:
            NotImplementedError: KBS không hỗ trợ trái phiếu chính phủ.
        """
        raise NotImplementedError(
            "KBS không cung cấp dữ liệu trái phiếu chính phủ. "
            "Sử dụng all_bonds() để lấy trái phiếu doanh nghiệp."
        )

    # ===================== Internal methods =====================

    def _get_full_stock_data(
        self,
        show_log: Optional[bool] = False,
    ) -> List[Dict]:
        """
        Internal method để lấy dữ liệu đầy đủ về tất cả chứng khoán từ /stock/search/data endpoint.

        Trả về danh sách chứng khoán với tất cả thông tin: symbol, name, nameEn, exchange, 
        type, index, re, ceiling, floor.

        Args:
            show_log: Hiển thị log debug. Mặc định False.

        Returns:
            List[Dict] chứa thông tin đầy đủ của tất cả chứng khoán, hoặc [] nếu lỗi.
        """
        url = _SEARCH_URL

        try:
            json_data = send_request(
                url=url,
                headers=self.headers,
                method='GET',
                payload=None,
                show_log=show_log,
                proxy_list=self.proxy_config.proxy_list,
                proxy_mode=self.proxy_config.proxy_mode,
                request_mode=self.proxy_config.request_mode,
            )

            if not json_data:
                raise ValueError("Không tìm thấy dữ liệu chứng khoán.")

            # KBS returns data in different formats
            if isinstance(json_data, list):
                stocks_data = json_data
            elif isinstance(json_data, dict) and 'data' in json_data:
                stocks_data = json_data['data']
            else:
                stocks_data = []

            if show_log:
                logger.info(f'Truy xuất thành công {len(stocks_data)} chứng khoán.')

            return stocks_data

        except Exception as e:
            if show_log:
                logger.error(f"Lỗi khi lấy dữ liệu chứng khoán: {str(e)}")
            return []

    def _get_symbols_by_group_internal(
        self,
        group: str,
        show_log: Optional[bool] = False,
    ) -> List[str]:
        """
        Internal method để lấy danh sách mã theo nhóm/sàn.

        Args:
            group: Tên nhóm hoặc sàn.
            show_log: Hiển thị log debug.

        Returns:
            List[str] chứa danh sách mã.
        """
        group_code = _GROUP_CODE.get(group, group)
        url = f'{_INDEX_URL}/{group_code}/stocks'

        try:
            json_data = send_request(
                url=url,
                headers=self.headers,
                method='GET',
                payload=None,
                show_log=show_log,
                proxy_list=self.proxy_config.proxy_list,
                proxy_mode=self.proxy_config.proxy_mode,
                request_mode=self.proxy_config.request_mode,
            )

            if not json_data:
                raise ValueError(f"Không tìm thấy dữ liệu cho nhóm {group}.")

            # KBS returns {"status": 200, "data": [...]}
            if isinstance(json_data, dict) and 'data' in json_data:
                symbols = json_data['data']
            elif isinstance(json_data, list):
                symbols = json_data
            else:
                symbols = []

            if show_log:
                logger.info(f'Truy xuất thành công {len(symbols)} mã từ nhóm {group}.')

            return symbols

        except Exception as e:
            if show_log:
                logger.error(f"Lỗi khi lấy dữ liệu từ nhóm {group}: {str(e)}")
            raise

    def _get_industries_internal(
        self,
        show_log: Optional[bool] = False,
    ) -> List[Dict]:
        """
        Internal method để lấy danh sách các ngành.

        Args:
            show_log: Hiển thị log debug.

        Returns:
            List[Dict] chứa thông tin ngành.
        """
        url = f'{_SECTOR_ALL_URL}'

        try:
            json_data = send_request(
                url=url,
                headers=self.headers,
                method='GET',
                payload=None,
                show_log=show_log,
                proxy_list=self.proxy_config.proxy_list,
                proxy_mode=self.proxy_config.proxy_mode,
                request_mode=self.proxy_config.request_mode,
            )

            if not json_data:
                raise ValueError("Không tìm thấy dữ liệu ngành.")

            # KBS returns a list of industries directly
            if isinstance(json_data, list):
                industries = json_data
            elif isinstance(json_data, dict) and 'data' in json_data:
                industries = json_data['data']
            else:
                industries = []

            if show_log:
                logger.info(f'Truy xuất thành công {len(industries)} ngành.')

            return industries

        except Exception as e:
            if show_log:
                logger.error(f"Lỗi khi lấy danh sách ngành: {str(e)}")
            # Return empty list instead of raising to allow graceful degradation
            return []

    def _get_symbols_by_industry_internal(
        self,
        industry_code: int,
        show_log: Optional[bool] = False,
    ) -> List[str]:
        """
        Internal method để lấy danh sách mã theo mã ngành.

        Args:
            industry_code: Mã ngành.
            show_log: Hiển thị log debug.

        Returns:
            List[str] chứa danh sách mã.
        """
        url = f'{_SECTOR_STOCK_URL}?code={industry_code}&l=1'

        try:
            json_data = send_request(
                url=url,
                headers=self.headers,
                method='GET',
                payload=None,
                show_log=show_log,
                proxy_list=self.proxy_config.proxy_list,
                proxy_mode=self.proxy_config.proxy_mode,
                request_mode=self.proxy_config.request_mode,
            )

            if not json_data:
                return []

            # Handle different response formats
            if isinstance(json_data, dict) and 'stocks' in json_data:
                # Extract stock symbols from the stocks list
                stocks = json_data['stocks']
                symbols = [stock['sb'] for stock in stocks if 'sb' in stock]
            elif isinstance(json_data, dict) and 'data' in json_data:
                symbols = json_data['data']
            elif isinstance(json_data, list):
                symbols = json_data
            else:
                symbols = []

            if show_log:
                logger.info(f'Truy xuất thành công {len(symbols)} mã từ ngành {industry_code}.')

            return symbols

        except Exception as e:
            if show_log:
                logger.error(f"Lỗi khi lấy mã từ ngành {industry_code}: {str(e)}")
            return []


# Register KBS Listing provider
from vnstock.core.registry import ProviderRegistry  # noqa: E402, F401
ProviderRegistry.register('listing', 'kbs', Listing)
