import json
import requests
import pandas as pd
from typing import Optional
from .const import _BASE_URL, _GRAPHQL_URL, _FINANCIAL_REPORT_PERIOD_MAP, _UNIT_MAP
from vnstock.core.utils.parser import get_asset_type, camel_to_snake
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers
# from vnstock.explorer.vci.financial import Finance

logger = get_logger(__name__)

class Company:
    """
    Class (lớp) quản lý các thông tin liên quan đến công ty từ nguồn dữ liệu VCI.

    Tham số:
        - symbol (str): Mã chứng khoán của công ty cần truy xuất thông tin.
        - random_agent (bool): Sử dụng user-agent ngẫu nhiên hoặc không. Mặc định là False.
    """
    def __init__(self, symbol, random_agent=False, to_df:Optional[bool]=True, show_log:Optional[bool]=False):
        self.symbol = symbol.upper()
        self.asset_type = get_asset_type(self.symbol)
        if self.asset_type not in ['stock']:
            raise ValueError("Mã chứng khoán không hợp lệ. Chỉ cổ phiếu mới có thông tin.")
        self.headers = get_headers(data_source='VCI', random_agent=random_agent)
        self.show_log = show_log
        self.to_df = to_df
        # self.finance = Finance(self.symbol)
        if not show_log:
            logger.setLevel('CRITICAL')

    def _fetch_data(self):
        url = "https://api.vietcap.com.vn/data-mt/graphql"

        payload = "{\"query\":\"query Query($ticker: String!, $lang: String!) {\\n  AnalysisReportFiles(ticker: $ticker, langCode: $lang) {\\n    date\\n    description\\n    link\\n    name\\n    __typename\\n  }\\n  News(ticker: $ticker, langCode: $lang) {\\n    id\\n    organCode\\n    ticker\\n    newsTitle\\n    newsSubTitle\\n    friendlySubTitle\\n    newsImageUrl\\n    newsSourceLink\\n    createdAt\\n    publicDate\\n    updatedAt\\n    langCode\\n    newsId\\n    newsShortContent\\n    newsFullContent\\n    closePrice\\n    referencePrice\\n    floorPrice\\n    ceilingPrice\\n    percentPriceChange\\n    __typename\\n  }\\n  TickerPriceInfo(ticker: $ticker) {\\n    financialRatio {\\n      yearReport\\n      lengthReport\\n      updateDate\\n      revenue\\n      revenueGrowth\\n      netProfit\\n      netProfitGrowth\\n      ebitMargin\\n      roe\\n      roic\\n      roa\\n      pe\\n      pb\\n      eps\\n      currentRatio\\n      cashRatio\\n      quickRatio\\n      interestCoverage\\n      ae\\n      fae\\n      netProfitMargin\\n      grossMargin\\n      ev\\n      issueShare\\n      ps\\n      pcf\\n      bvps\\n      evPerEbitda\\n      at\\n      fat\\n      acp\\n      dso\\n      dpo\\n      epsTTM\\n      charterCapital\\n      RTQ4\\n      charterCapitalRatio\\n      RTQ10\\n      dividend\\n      ebitda\\n      ebit\\n      le\\n      de\\n      ccc\\n      RTQ17\\n      __typename\\n    }\\n    ticker\\n    exchange\\n    ev\\n    ceilingPrice\\n    floorPrice\\n    referencePrice\\n    openPrice\\n    matchPrice\\n    closePrice\\n    priceChange\\n    percentPriceChange\\n    highestPrice\\n    lowestPrice\\n    totalVolume\\n    highestPrice1Year\\n    lowestPrice1Year\\n    percentLowestPriceChange1Year\\n    percentHighestPriceChange1Year\\n    foreignTotalVolume\\n    foreignTotalRoom\\n    averageMatchVolume2Week\\n    foreignHoldingRoom\\n    currentHoldingRatio\\n    maxHoldingRatio\\n    __typename\\n  }\\n  Subsidiary(ticker: $ticker) {\\n    id\\n    organCode\\n    subOrganCode\\n    percentage\\n    subOrListingInfo {\\n      enOrganName\\n      organName\\n      __typename\\n    }\\n    __typename\\n  }\\n  Affiliate(ticker: $ticker) {\\n    id\\n    organCode\\n    subOrganCode\\n    percentage\\n    subOrListingInfo {\\n      enOrganName\\n      organName\\n      __typename\\n    }\\n    __typename\\n  }\\n  CompanyListingInfo(ticker: $ticker) {\\n    id\\n    issueShare\\n    en_History\\n    history\\n    en_CompanyProfile\\n    companyProfile\\n    icbName3\\n    enIcbName3\\n    icbName2\\n    enIcbName2\\n    icbName4\\n    enIcbName4\\n    financialRatio {\\n      id\\n      ticker\\n      issueShare\\n      charterCapital\\n      __typename\\n    }\\n    __typename\\n  }\\n  OrganizationManagers(ticker: $ticker) {\\n    id\\n    ticker\\n    fullName\\n    positionName\\n    positionShortName\\n    en_PositionName\\n    en_PositionShortName\\n    updateDate\\n    percentage\\n    quantity\\n    __typename\\n  }\\n  OrganizationShareHolders(ticker: $ticker) {\\n    id\\n    ticker\\n    ownerFullName\\n    en_OwnerFullName\\n    quantity\\n    percentage\\n    updateDate\\n    __typename\\n  }\\n  OrganizationResignedManagers(ticker: $ticker) {\\n    id\\n    ticker\\n    fullName\\n    positionName\\n    positionShortName\\n    en_PositionName\\n    en_PositionShortName\\n    updateDate\\n    percentage\\n    quantity\\n    __typename\\n  }\\n  OrganizationEvents(ticker: $ticker) {\\n    id\\n    organCode\\n    ticker\\n    eventTitle\\n    en_EventTitle\\n    publicDate\\n    issueDate\\n    sourceUrl\\n    eventListCode\\n    ratio\\n    value\\n    recordDate\\n    exrightDate\\n    eventListName\\n    en_EventListName\\n    __typename\\n  }\\n}\\n\",\"variables\":{\"ticker\":\"VCI\",\"lang\":\"vi\"}}"
        if self.show_log:
            logger.debug(f"Requesting data for {self.symbol} from {url}. payload: {payload}")

        # load payload to dict
        payload = json.loads(payload)
        payload['variables']['ticker'] = self.symbol
        # convert dict to json string
        payload = json.dumps(payload)

        response = requests.request("POST", url, headers=self.headers, data=payload)
        if self.show_log:
            logger.debug(f"Response: {response.text}")
        if response.status_code != 200:
            logger.error(f"Request failed with status code {response.status_code}. Details: {response.text}")
        data = response.json()['data']
        return data
