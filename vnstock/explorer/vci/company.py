"""
Module quản lý thông tin công ty từ nguồn dữ liệu VCI.
"""

import json
import pandas as pd
from typing import Dict, Optional, Union, List
from vnstock.core.utils import client
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers
from vnstock.core.utils.transform import clean_html_dict, flatten_dict_to_df, flatten_list_to_df, reorder_cols, drop_cols_by_pattern
from vnstock.core.utils.parser import get_asset_type, camel_to_snake
from vnai import optimize_execution  # Import the decorator from vnai package
from .const import _GRAPHQL_URL, _PRICE_INFO_MAP
import copy

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
        self.raw_data = self._fetch_data()
        
        if not show_log:
            logger.setLevel('CRITICAL')

    def _fetch_data(self) -> Dict:
        """
        Phương thức riêng để lấy dữ liệu công ty từ nguồn VCI.
        
        Returns:
            Dict: Dữ liệu thô về công ty từ API.
        """
        url = _GRAPHQL_URL

        # GraphQL query for company data
        payload = "{\"query\":\"query Query($ticker: String!, $lang: String!) {\\n  AnalysisReportFiles(ticker: $ticker, langCode: $lang) {\\n    date\\n    description\\n    link\\n    name\\n    __typename\\n  }\\n  News(ticker: $ticker, langCode: $lang) {\\n    id\\n    organCode\\n    ticker\\n    newsTitle\\n    newsSubTitle\\n    friendlySubTitle\\n    newsImageUrl\\n    newsSourceLink\\n    createdAt\\n    publicDate\\n    updatedAt\\n    langCode\\n    newsId\\n    newsShortContent\\n    newsFullContent\\n    closePrice\\n    referencePrice\\n    floorPrice\\n    ceilingPrice\\n    percentPriceChange\\n    __typename\\n  }\\n  TickerPriceInfo(ticker: $ticker) {\\n    financialRatio {\\n      yearReport\\n      lengthReport\\n      updateDate\\n      revenue\\n      revenueGrowth\\n      netProfit\\n      netProfitGrowth\\n      ebitMargin\\n      roe\\n      roic\\n      roa\\n      pe\\n      pb\\n      eps\\n      currentRatio\\n      cashRatio\\n      quickRatio\\n      interestCoverage\\n      ae\\n      fae\\n      netProfitMargin\\n      grossMargin\\n      ev\\n      issueShare\\n      ps\\n      pcf\\n      bvps\\n      evPerEbitda\\n      at\\n      fat\\n      acp\\n      dso\\n      dpo\\n      epsTTM\\n      charterCapital\\n      RTQ4\\n      charterCapitalRatio\\n      RTQ10\\n      dividend\\n      ebitda\\n      ebit\\n      le\\n      de\\n      ccc\\n      RTQ17\\n      __typename\\n    }\\n    ticker\\n    exchange\\n    ev\\n    ceilingPrice\\n    floorPrice\\n    referencePrice\\n    openPrice\\n    matchPrice\\n    closePrice\\n    priceChange\\n    percentPriceChange\\n    highestPrice\\n    lowestPrice\\n    totalVolume\\n    highestPrice1Year\\n    lowestPrice1Year\\n    percentLowestPriceChange1Year\\n    percentHighestPriceChange1Year\\n    foreignTotalVolume\\n    foreignTotalRoom\\n    averageMatchVolume2Week\\n    foreignHoldingRoom\\n    currentHoldingRatio\\n    maxHoldingRatio\\n    __typename\\n  }\\n  Subsidiary(ticker: $ticker) {\\n    id\\n    organCode\\n    subOrganCode\\n    percentage\\n    subOrListingInfo {\\n      enOrganName\\n      organName\\n      __typename\\n    }\\n    __typename\\n  }\\n  Affiliate(ticker: $ticker) {\\n    id\\n    organCode\\n    subOrganCode\\n    percentage\\n    subOrListingInfo {\\n      enOrganName\\n      organName\\n      __typename\\n    }\\n    __typename\\n  }\\n  CompanyListingInfo(ticker: $ticker) {\\n    id\\n    issueShare\\n    en_History\\n    history\\n    en_CompanyProfile\\n    companyProfile\\n    icbName3\\n    enIcbName3\\n    icbName2\\n    enIcbName2\\n    icbName4\\n    enIcbName4\\n    financialRatio {\\n      id\\n      ticker\\n      issueShare\\n      charterCapital\\n      __typename\\n    }\\n    __typename\\n  }\\n  OrganizationManagers(ticker: $ticker) {\\n    id\\n    ticker\\n    fullName\\n    positionName\\n    positionShortName\\n    en_PositionName\\n    en_PositionShortName\\n    updateDate\\n    percentage\\n    quantity\\n    __typename\\n  }\\n  OrganizationShareHolders(ticker: $ticker) {\\n    id\\n    ticker\\n    ownerFullName\\n    en_OwnerFullName\\n    quantity\\n    percentage\\n    updateDate\\n    __typename\\n  }\\n  OrganizationResignedManagers(ticker: $ticker) {\\n    id\\n    ticker\\n    fullName\\n    positionName\\n    positionShortName\\n    en_PositionName\\n    en_PositionShortName\\n    updateDate\\n    percentage\\n    quantity\\n    __typename\\n  }\\n  OrganizationEvents(ticker: $ticker) {\\n    id\\n    organCode\\n    ticker\\n    eventTitle\\n    en_EventTitle\\n    publicDate\\n    issueDate\\n    sourceUrl\\n    eventListCode\\n    ratio\\n    value\\n    recordDate\\n    exrightDate\\n    eventListName\\n    en_EventListName\\n    __typename\\n  }\\n}\\n\",\"variables\":{\"ticker\":\"VCI\",\"lang\":\"vi\"}}"
        
        payload = json.loads(payload)
        payload['variables']['ticker'] = self.symbol
        
        if self.show_log:
            logger.debug(f"Requesting data for {self.symbol} from {url}. payload: {payload}")

        # Use centralized API client instead of direct requests
        response_data = client.send_request(
            url=url,
            headers=self.headers,
            method="POST",
            payload=payload,
            show_log=self.show_log
        )
        
        return response_data['data']

    def _process_data(self, data: Dict, data_key: str, 
                      columns_dict: Optional[Dict] = None) -> pd.DataFrame:
        """
        Xử lý dữ liệu công ty từ API của VCI và chuyển đổi thành DataFrame.

        Tham số:
            - data (Dict): Dữ liệu từ API của VCI.
            - data_key (str): Khóa của dữ liệu cần xử lý.
            - columns_dict (Dict, optional): Từ điển các cột cần đổi tên.

        Returns:
            pd.DataFrame: DataFrame đã xử lý.
        """
        segment_data = data[data_key]

        # Convert to DataFrame
        df = pd.DataFrame(segment_data)

        # Rename columns to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]

        # Rename columns if specified
        if columns_dict:
            df = df.rename(columns=columns_dict)

        return df
    
    def _parse_price_info(self) -> tuple:
        """
        Phân tách dữ liệu giá và tỷ lệ tài chính từ thông tin giá.
        
        Returns:
            tuple: (price_data, ratio_data) - Bộ dữ liệu giá và tỷ lệ tài chính.
        """
        # Process raw_data['TickerPriceInfo]['financialRatio'] separately from raw_data['TickerPriceInfo]
        price_data = copy.deepcopy(self.raw_data['TickerPriceInfo'])
        ratio_data = pd.DataFrame(price_data['financialRatio'], index=[0])
        
        # Remove key 'financialRatio' from price_data dict
        price_data.pop('financialRatio')
        price_data = pd.DataFrame(price_data, index=[0])
        
        return price_data, ratio_data
    
    @optimize_execution("VCI")
    def overview(self) -> pd.DataFrame:
        """
        Truy xuất thông tin tổng quan của công ty.
        
        Returns:
            pd.DataFrame: DataFrame chứa thông tin tổng quan của công ty.
        """
        data = self.raw_data['CompanyListingInfo']
        clean_data = clean_html_dict(data)
        df = flatten_dict_to_df(clean_data, 'financialRatio')
        
        # Replace '\n' with ' ' in all string columns
        # df = df.map(lambda x: x.replace('\n', ' ') if isinstance(x, str) else x) # This is for pandas 2.x
        df = df.applymap(lambda x: x.replace('\n', ' ') if isinstance(x, str) else x) # This can be used for pandas 1.x and 2.x
        
        # Convert to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]
        
        # Drop columns with prefixes 'en_', '__' and these specific columns
        df = drop_cols_by_pattern(df, ['en_', '__', '_ratio_id'])
        
        # Rename ticker column to symbol
        df = df.rename(columns={'ticker': 'symbol'})
        
        # Reorder columns to have symbol first
        df = reorder_cols(df, ['symbol'], position='first')
        
        return df

    @optimize_execution("VCI")
    def shareholders(self) -> pd.DataFrame:
        """
        Truy xuất thông tin cổ đông của công ty.
        
        Returns:
            pd.DataFrame: DataFrame chứa thông tin cổ đông của công ty.
        """
        df = self._process_data(self.raw_data, 'OrganizationShareHolders')
        
        # Drop unnecessary columns
        df = drop_cols_by_pattern(df, ['__typename', 'ticker', 'en_'])
        
        # Convert update_date from timestamp to date string %Y-%m-%d
        df['update_date'] = pd.to_datetime(df['update_date'], unit='ms').dt.strftime('%Y-%m-%d')
        
        # Rename columns for clarity
        df = df.rename(columns={
            'owner_full_name': 'share_holder', 
            'percentage': 'share_own_percent'
        })
        
        return df
    
    @optimize_execution("VCI")
    def officers(self, filter_by: str = 'working') -> pd.DataFrame:
        """
        Truy xuất thông tin lãnh đạo công ty.

        Tham số:
            - filter_by (str): Lọc lãnh đạo đang làm việc hoặc đã từ nhiệm hoặc tất cả.
                - 'working': Lọc lãnh đạo đang làm việc.
                - 'resigned': Lọc lãnh đạo đã từ nhiệm.
                - 'all': Lọc tất cả lãnh đạo.

        Returns:
            pd.DataFrame: DataFrame chứa thông tin lãnh đạo của công ty.
        """
        if filter_by not in ['working', 'resigned', 'all']:
            raise ValueError("filter_by chỉ nhận giá trị 'working' hoặc 'resigned' hoặc 'all'")
        
        if filter_by == 'working':
            df = self._process_data(self.raw_data, 'OrganizationManagers')
        elif filter_by == 'resigned':
            df = self._process_data(self.raw_data, 'OrganizationResignedManagers')
        else:
            # Combine both working and resigned officers
            working_df = self._process_data(self.raw_data, 'OrganizationManagers')
            working_df['type'] = 'đang làm việc'
            resigned_df = self._process_data(self.raw_data, 'OrganizationResignedManagers')
            resigned_df['type'] = 'đã từ nhiệm'
            df = pd.concat([working_df, resigned_df])
        
        # Drop unnecessary columns
        df = drop_cols_by_pattern(df, ['en_', '__', 'ticker'])
        
        # Reorder columns
        df = reorder_cols(df, ['symbol'], position='first')
        
        # Rename columns for clarity
        df = df.rename(columns={
            'full_name': 'officer_name', 
            'position_name': 'officer_position', 
            'percentage': 'officer_own_percent'
        })
        
        # Convert update_date from timestamp to date string
        df['update_date'] = pd.to_datetime(df['update_date'], unit='ms').dt.strftime('%Y-%m-%d')
        
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
        if filter_by not in ['all', 'subsidiary']:
            raise ValueError("filter_by chỉ nhận giá trị 'all' hoặc 'subsidiary'")
        
        df = self.raw_data['Subsidiary']
        df = flatten_list_to_df(df, 'subOrListingInfo')
        
        # Convert column names to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]
        
        # Drop unnecessary columns
        df = drop_cols_by_pattern(df, ['__typename', 'en_'])
        df = df.drop(columns=['organ_code'])
        
        # Rename percentage to ownership_percent for clarity
        df = df.rename(columns={'percentage': 'ownership_percent'})
        df['type'] = 'công ty con'

        if filter_by == 'subsidiary':
            return df
        elif filter_by == 'all':
            affiliate_df = self.affiliate()
            affiliate_df['type'] = 'công ty liên kết'
            combine_df = pd.concat([df, affiliate_df])
            return combine_df
        
    @optimize_execution("VCI")
    def affiliate(self) -> pd.DataFrame:
        """
        Truy xuất thông tin công ty liên kết của công ty.
        
        Returns:
            pd.DataFrame: DataFrame chứa thông tin công ty liên kết.
        """
        data = self.raw_data['Affiliate']
        df = flatten_list_to_df(data, 'subOrListingInfo')
        
        # Convert column names to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]
        
        # Drop unnecessary columns
        df = drop_cols_by_pattern(df, ['en_', '__typename'])
        df = df.drop(columns=['organ_code'])
        
        # Reorder columns
        df = reorder_cols(df, ['id', 'sub_organ_code', 'organ_name'], position='first')
        
        # Rename percentage to ownership_percent for clarity
        df = df.rename(columns={'percentage': 'ownership_percent'})
        
        return df
      
    @optimize_execution("VCI")
    def news(self) -> pd.DataFrame:
        """
        Truy xuất tin tức liên quan đến công ty.
        
        Returns:
            pd.DataFrame: DataFrame chứa tin tức liên quan đến công ty.
        """
        df = self._process_data(self.raw_data, 'News')
        
        # Rename columns according to the price info mapping
        for col, new_col in _PRICE_INFO_MAP.items():
            if col in df.columns:
                df = df.rename(columns={col: new_col})
        
        # Drop unnecessary columns
        df = df.drop(columns=['organ_code', 'symbol', '__typename'])
        
        return df
    
    @optimize_execution("VCI")
    def events(self) -> pd.DataFrame:
        """
        Truy xuất các sự kiện của công ty.
        
        Returns:
            pd.DataFrame: DataFrame chứa các sự kiện của công ty.
        """
        df = self._process_data(self.raw_data, 'OrganizationEvents')
        
        # Rename columns according to the price info mapping
        for col, new_col in _PRICE_INFO_MAP.items():
            if col in df.columns:
                df = df.rename(columns={col: new_col})
        
        # Drop unnecessary columns
        df = df.drop(columns=['organ_code', 'symbol', '__typename'])
        
        # Convert date columns from timestamp to date string
        date_columns = ['public_date', 'issue_date', 'record_date', 'exright_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], unit='ms').dt.strftime('%Y-%m-%d')
        
        return df
    
    @optimize_execution("VCI")
    def reports(self) -> pd.DataFrame:
        """
        Truy xuất báo cáo phân tích về công ty.
        
        Returns:
            pd.DataFrame: DataFrame chứa các báo cáo phân tích về công ty.
        """
        df = self._process_data(self.raw_data, 'AnalysisReportFiles')
        
        # Drop __typename column if it exists
        if '__typename' in df.columns:
            df = df.drop(columns=['__typename'])
        
        # Convert date from timestamp to date string if it's in timestamp format
        if 'date' in df.columns and df['date'].dtype in [int, float]:
            df['date'] = pd.to_datetime(df['date'], unit='ms').dt.strftime('%Y-%m-%d')
        
        return df

    @optimize_execution("VCI")
    def trading_stats(self) -> pd.DataFrame:
        """
        Truy xuất thống kê giao dịch của công ty.
        
        Returns:
            pd.DataFrame: DataFrame chứa thống kê giao dịch của công ty.
        """
        price_data, _ = self._parse_price_info()
        df = pd.DataFrame(price_data)
        
        # Convert column names to snake_case
        df.columns = [camel_to_snake(col) for col in df.columns]
        
        # Drop __typename column
        df = drop_cols_by_pattern(df, ['__typename'])
        
        # Rename columns according to the price info mapping
        for col, new_col in _PRICE_INFO_MAP.items():
            if col in df.columns:
                df = df.rename(columns={col: new_col})
        
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
        _, financial_ratio_data = self._parse_price_info()
        
        # Convert column names to snake_case
        financial_ratio_data.columns = [camel_to_snake(col) for col in financial_ratio_data.columns]
        
        # Drop __typename column
        df = drop_cols_by_pattern(financial_ratio_data, ['__typename'])
        
        # Add symbol column
        df['symbol'] = self.symbol
        
        # Reorder to have symbol first
        df = reorder_cols(df, cols=['symbol'], position='first')
        
        return df
