import pandas as pd
import json
import requests
from typing import Optional
from .const import _BASE_URL, _GRAPHQL_URL, _FINANCIAL_REPORT_PERIOD_MAP, _UNIT_MAPPING
from vnstock3.core.utils.parser import get_asset_type, camel_to_snake
from vnstock3.core.utils.logger import get_logger
from vnstock3.core.utils.user_agent import get_headers

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

    def _fetch_data(self):
        url = "https://api.vietcap.com.vn/data-mt/graphql"

        payload = "{\"query\":\"query Query($ticker: String!, $lang: String!) {\\n  AnalysisReportFiles(ticker: $ticker, langCode: $lang) {\\n    date\\n    description\\n    link\\n    name\\n    __typename\\n  }\\n  News(ticker: $ticker, langCode: $lang) {\\n    id\\n    organCode\\n    ticker\\n    newsTitle\\n    newsSubTitle\\n    friendlySubTitle\\n    newsImageUrl\\n    newsSourceLink\\n    createdAt\\n    publicDate\\n    updatedAt\\n    langCode\\n    newsId\\n    newsShortContent\\n    newsFullContent\\n    closePrice\\n    referencePrice\\n    floorPrice\\n    ceilingPrice\\n    percentPriceChange\\n    __typename\\n  }\\n  TickerPriceInfo(ticker: $ticker) {\\n    financialRatio {\\n      yearReport\\n      lengthReport\\n      updateDate\\n      revenue\\n      revenueGrowth\\n      netProfit\\n      netProfitGrowth\\n      ebitMargin\\n      roe\\n      roic\\n      roa\\n      pe\\n      pb\\n      eps\\n      currentRatio\\n      cashRatio\\n      quickRatio\\n      interestCoverage\\n      ae\\n      fae\\n      netProfitMargin\\n      grossMargin\\n      ev\\n      issueShare\\n      ps\\n      pcf\\n      bvps\\n      evPerEbitda\\n      at\\n      fat\\n      acp\\n      dso\\n      dpo\\n      epsTTM\\n      charterCapital\\n      RTQ4\\n      charterCapitalRatio\\n      RTQ10\\n      dividend\\n      ebitda\\n      ebit\\n      le\\n      de\\n      ccc\\n      RTQ17\\n      __typename\\n    }\\n    ticker\\n    exchange\\n    ev\\n    ceilingPrice\\n    floorPrice\\n    referencePrice\\n    openPrice\\n    matchPrice\\n    closePrice\\n    priceChange\\n    percentPriceChange\\n    highestPrice\\n    lowestPrice\\n    totalVolume\\n    highestPrice1Year\\n    lowestPrice1Year\\n    percentLowestPriceChange1Year\\n    percentHighestPriceChange1Year\\n    foreignTotalVolume\\n    foreignTotalRoom\\n    averageMatchVolume2Week\\n    foreignHoldingRoom\\n    currentHoldingRatio\\n    maxHoldingRatio\\n    __typename\\n  }\\n  Subsidiary(ticker: $ticker) {\\n    id\\n    organCode\\n    subOrganCode\\n    percentage\\n    subOrListingInfo {\\n      enOrganName\\n      organName\\n      __typename\\n    }\\n    __typename\\n  }\\n  Affiliate(ticker: $ticker) {\\n    id\\n    organCode\\n    subOrganCode\\n    percentage\\n    subOrListingInfo {\\n      enOrganName\\n      organName\\n      __typename\\n    }\\n    __typename\\n  }\\n  CompanyListingInfo(ticker: $ticker) {\\n    id\\n    issueShare\\n    en_History\\n    history\\n    en_CompanyProfile\\n    companyProfile\\n    icbName3\\n    enIcbName3\\n    icbName2\\n    enIcbName2\\n    icbName4\\n    enIcbName4\\n    financialRatio {\\n      id\\n      ticker\\n      issueShare\\n      charterCapital\\n      __typename\\n    }\\n    __typename\\n  }\\n  OrganizationManagers(ticker: $ticker) {\\n    id\\n    ticker\\n    fullName\\n    positionName\\n    positionShortName\\n    en_PositionName\\n    en_PositionShortName\\n    updateDate\\n    percentage\\n    quantity\\n    __typename\\n  }\\n  OrganizationShareHolders(ticker: $ticker) {\\n    id\\n    ticker\\n    ownerFullName\\n    en_OwnerFullName\\n    quantity\\n    percentage\\n    updateDate\\n    __typename\\n  }\\n  OrganizationResignedManagers(ticker: $ticker) {\\n    id\\n    ticker\\n    fullName\\n    positionName\\n    positionShortName\\n    en_PositionName\\n    en_PositionShortName\\n    updateDate\\n    percentage\\n    quantity\\n    __typename\\n  }\\n  OrganizationEvents(ticker: $ticker) {\\n    id\\n    organCode\\n    ticker\\n    eventTitle\\n    en_EventTitle\\n    publicDate\\n    issueDate\\n    sourceUrl\\n    eventListCode\\n    ratio\\n    value\\n    recordDate\\n    exrightDate\\n    eventListName\\n    en_EventListName\\n    __typename\\n  }\\n}\\n\",\"variables\":{\"ticker\":\"VCI\",\"lang\":\"vi\"}}"
        if self.show_log:
            logger.debug(f"Requesting data for {self.symbol} from {url}. payload: {payload}")
        response = requests.request("POST", url, headers=self.headers, data=payload)
        if self.show_log:
            logger.debug(f"Response: {response.text}")
        if response.status_code != 200:
            logger.error(f"Request failed with status code {response.status_code}. Details: {response.text}")
        data = response.json()['data']
        return data
    
    
class Finance ():
    """
    Truy xuất thông tin báo cáo tài chính của một công ty theo mã chứng khoán từ nguồn dữ liệu VCI.

    Tham số:
        - symbol (str): Mã chứng khoán của công ty cần truy xuất thông tin.
        - period (str): Chu kỳ báo cáo tài chính cần truy xuất. Mặc định là 'quarterly'.
    """

    def __init__(self, symbol, period:Optional[str]='quarter', get_all:Optional[bool]=True):
        self.symbol = symbol.upper()
        self.asset_type = get_asset_type(self.symbol)
        self.headers = get_headers(data_source='VCI')
        # validate input for period
        if period not in ['year', 'quarter']:
            raise ValueError("Kỳ báo cáo tài chính không hợp lệ. Chỉ chấp nhận 'year' hoặc 'quarter'.")
        # if asset_type is not stock, raise error
        if self.asset_type not in ['stock']:
            raise ValueError("Mã chứng khoán không hợp lệ. Chỉ cổ phiếu mới có thông tin.")
        self.period = _FINANCIAL_REPORT_PERIOD_MAP.get(period)
        self.get_all = get_all

    def _get_ratio_dict(self, show_log:Optional[bool]=False, get_all:Optional[bool]=False):
        payload = "{\"query\":\"query Query {\\n  ListFinancialRatio {\\n    id\\n    type\\n    name\\n    unit\\n    isDefault\\n    fieldName\\n    en_Type\\n    en_Name\\n    tagName\\n    comTypeCode\\n    order\\n    __typename\\n  }\\n}\\n\",\"variables\":{}}"
        if show_log:
            logger.debug(f"Requesting financial ratio data from {_GRAPHQL_URL}. payload: {payload}")
        response = requests.request("POST", _GRAPHQL_URL, headers=self.headers, data=payload)
        if response.status_code != 200:
            logger.error(f"Request failed with status code {response.status_code}. Details: {response.text}")
        data = response.json()['data']['ListFinancialRatio']
        df = pd.DataFrame(data)
        df.columns = [camel_to_snake(col) for col in df.columns]
        effective_get_all = get_all if get_all is not None else self.get_all
        selected_columns = ['field_name', 'name', 'en__name', 'type', 'order', 'unit']
        df['unit'] = df['unit'].map(_UNIT_MAPPING)
        if effective_get_all is False:
            df = df[selected_columns]
        df.columns = [col.replace('__', '_') for col in df.columns]
        return df

    def _get_report (self, period:Optional[str]=None, lang:Optional[str]='en', show_log:Optional[bool]=False):
        # if lange not in ['vi', 'en'] then raise error
        if lang not in ['vi', 'en']:
            raise ValueError("Ngôn ngữ không hợp lệ. Chỉ chấp nhận 'vi' hoặc 'en'.")
        effective_period = _FINANCIAL_REPORT_PERIOD_MAP.get(period, period) if period else self.period
        payload = "{\"query\":\"fragment Ratios on CompanyFinancialRatio {\\n  ticker\\n  yearReport\\n  lengthReport\\n  updateDate\\n  revenue\\n  revenueGrowth\\n  netProfit\\n  netProfitGrowth\\n  ebitMargin\\n  roe\\n  roic\\n  roa\\n  pe\\n  pb\\n  eps\\n  currentRatio\\n  cashRatio\\n  quickRatio\\n  interestCoverage\\n  ae\\n  netProfitMargin\\n  grossMargin\\n  ev\\n  issueShare\\n  ps\\n  pcf\\n  bvps\\n  evPerEbitda\\n  BSA1\\n  BSA2\\n  BSA5\\n  BSA8\\n  BSA10\\n  BSA159\\n  BSA16\\n  BSA22\\n  BSA23\\n  BSA24\\n  BSA162\\n  BSA27\\n  BSA29\\n  BSA43\\n  BSA46\\n  BSA50\\n  BSA209\\n  BSA53\\n  BSA54\\n  BSA55\\n  BSA56\\n  BSA58\\n  BSA67\\n  BSA71\\n  BSA173\\n  BSA78\\n  BSA79\\n  BSA80\\n  BSA175\\n  BSA86\\n  BSA90\\n  BSA96\\n  CFA21\\n  CFA22\\n  at\\n  fat\\n  acp\\n  dso\\n  dpo\\n  ccc\\n  de\\n  le\\n  ebitda\\n  ebit\\n  dividend\\n  RTQ10\\n  charterCapitalRatio\\n  RTQ4\\n  epsTTM\\n  charterCapital\\n  fae\\n  RTQ17\\n  CFA26\\n  CFA6\\n  CFA9\\n  BSA85\\n  CFA36\\n  BSB98\\n  BSB101\\n  BSA89\\n  CFA34\\n  CFA14\\n  ISB34\\n  ISB27\\n  ISA23\\n  ISS152\\n  ISA102\\n  CFA27\\n  CFA12\\n  CFA28\\n  BSA18\\n  BSB102\\n  BSB110\\n  BSB108\\n  CFA23\\n  ISB41\\n  BSB103\\n  BSA40\\n  BSB99\\n  CFA16\\n  CFA18\\n  CFA3\\n  ISB30\\n  BSA33\\n  ISB29\\n  CFS200\\n  ISA2\\n  CFA24\\n  BSB105\\n  CFA37\\n  ISS141\\n  BSA95\\n  CFA10\\n  ISA4\\n  BSA82\\n  CFA25\\n  BSB111\\n  ISI64\\n  BSB117\\n  ISA20\\n  CFA19\\n  ISA6\\n  ISA3\\n  BSB100\\n  ISB31\\n  ISB38\\n  ISB26\\n  BSA210\\n  CFA20\\n  CFA35\\n  ISA17\\n  ISS148\\n  BSB115\\n  ISA9\\n  CFA4\\n  ISA7\\n  CFA5\\n  ISA22\\n  CFA8\\n  CFA33\\n  CFA29\\n  BSA30\\n  BSA84\\n  BSA44\\n  BSB107\\n  ISB37\\n  ISA8\\n  BSB109\\n  ISA19\\n  ISB36\\n  ISA13\\n  ISA1\\n  BSB121\\n  ISA14\\n  BSB112\\n  ISA21\\n  ISA10\\n  CFA11\\n  ISA12\\n  BSA15\\n  BSB104\\n  BSA92\\n  BSB106\\n  BSA94\\n  ISA18\\n  CFA17\\n  ISI87\\n  BSB114\\n  ISA15\\n  BSB116\\n  ISB28\\n  BSB97\\n  CFA15\\n  ISA11\\n  ISB33\\n  BSA47\\n  ISB40\\n  ISB39\\n  CFA7\\n  CFA13\\n  ISS146\\n  ISB25\\n  BSA45\\n  BSB118\\n  CFA1\\n  CFS191\\n  ISB35\\n  CFB65\\n  CFA31\\n  BSB113\\n  ISB32\\n  ISA16\\n  CFS210\\n  BSA48\\n  BSA36\\n  ISI97\\n  CFA30\\n  CFA2\\n  CFB80\\n  CFA38\\n  CFA32\\n  ISA5\\n  BSA49\\n  CFB64\\n  __typename\\n}\\n\\nquery Query($ticker: String!, $period: String!) {\\n  CompanyFinancialRatio(ticker: $ticker, period: $period) {\\n    ratio {\\n      ...Ratios\\n      __typename\\n    }\\n    period\\n    __typename\\n  }\\n}\\n\",\"variables\":{\"ticker\":\"VCI\",\"period\":\"Q\"}}"
        payload_json = json.loads(payload)
        payload_json['variables']['ticker'] = self.symbol
        payload_json['variables']['period'] = effective_period
        # convert payload_json to string
        payload_json = json.dumps(payload_json)

        response = requests.post(_GRAPHQL_URL, data=payload_json, headers=self.headers)
        if show_log:
            logger.debug(f"Requesting financial report data from {_GRAPHQL_URL}. payload: {payload_json}")
        if response.status_code != 200:
            logger.error(f"Request failed with status code {response.status_code}. Details: {response.text}")

        data = response.json()['data']['CompanyFinancialRatio']['ratio']
        ratio_df = pd.DataFrame(data)

        if lang == 'vi':
            ratio_df = ratio_df.rename(columns={'ticker': 'CP', 'yearReport': 'Năm', 'lengthReport': 'Kỳ'})
            index_part = ratio_df[['CP', 'Năm', 'Kỳ']]
            target_col_name = 'name'
        elif lang == 'en':
            index_part = ratio_df[['ticker', 'yearReport', 'lengthReport']]
            target_col_name = 'en_name'

        # Create a dictionary to map field_name to report type
        mapping_df = self._get_ratio_dict(get_all=False)          

        type_mapping = dict(zip(mapping_df[target_col_name], mapping_df['type']))
        # add a translation layer mapping for name and en_name
        columns_translate = dict(zip(mapping_df['name'], mapping_df['en_name']))

        logger.debug(f"Type mapping: {type_mapping}")

        # Organize columns in ratio_df into different reports based on type
        reports = {}
        for field, report_type in type_mapping.items():
            if report_type not in reports:
                reports[report_type] = [field]
            else:
                reports[report_type].append(field)

        # Rename columns in ratio_df based on mapping_df's 'name'
        name_mapping = dict(zip(mapping_df['field_name'], mapping_df[target_col_name]))
        logger.debug(f"Name mapping: {name_mapping}")
        ratio_df.rename(columns=name_mapping, inplace=True)

        # Create DataFrames for each report type with exception handling
        report_dfs = {}
        for report_type, columns in reports.items():
            try:
                # Filter the DataFrame only for columns that exist in ratio_df
                filtered_columns = [col for col in columns if col in ratio_df.columns]
                report_dfs[report_type] = ratio_df[filtered_columns]
            except KeyError as e:
                print(f"Failed to create DataFrame for {report_type} due to missing columns: {e}")

        # Define the primary report types
        primary_reports = [
            'Chỉ tiêu cân đối kế toán', 
            'Chỉ tiêu lưu chuyển tiền tệ', 
            'Chỉ tiêu kết quả kinh doanh'
        ]

        # Splitting the reports
        primary_dfs = {key: report_dfs[key] for key in primary_reports}
        other_reports = {key: report_dfs[key] for key in report_dfs if key not in primary_reports}

        # Merge all other reports into a single DataFrame with MultiIndex columns
        merged_other_reports = pd.concat(other_reports.values(), axis=1, keys=other_reports.keys())

        primary_dfs = {key: pd.concat([index_part, value], axis=1) for key, value in primary_dfs.items()}

        # Convert 'index_part' to MultiIndex with blank top level
        index_part.columns = pd.MultiIndex.from_tuples([('Meta', col) for col in index_part.columns])
        merged_other_reports = pd.concat([index_part, merged_other_reports], axis=1)

        def multi_level_columns_translate(col, translation_dict):
            # Modify the lowest level while keeping the upper level(s) the same
            upper_levels = col[:-1]
            lowest_level = col[-1]
            new_lowest_level = translation_dict.get(lowest_level, lowest_level)  # Apply translation or use the original
            return upper_levels + (new_lowest_level,)

        if lang == 'en':
            # Apply the columns_translate function to all columns
            merged_other_reports.columns = pd.MultiIndex.from_tuples(
                [multi_level_columns_translate(col, columns_translate) for col in merged_other_reports.columns]
            )

        return primary_dfs, merged_other_reports\
        
    def _process_report (self, report_key:str , period:Optional[str]=None, lang:Optional[str]='en', dropna:Optional[bool]=False, show_log:Optional[bool]=False):
        # validate report_key should be in 'Chỉ tiêu kết quả kinh doanh', 'Chỉ tiêu cân đối kế toán', 'Chỉ tiêu lưu chuyển tiền tệ'
        if report_key not in ['Chỉ tiêu kết quả kinh doanh', 'Chỉ tiêu cân đối kế toán', 'Chỉ tiêu lưu chuyển tiền tệ']:
            raise ValueError("Báo cáo không hợp lệ. Chỉ chấp nhận 'Chỉ tiêu kết quả kinh doanh', 'Chỉ tiêu cân đối kế toán', 'Chỉ tiêu lưu chuyển tiền tệ'.")

        effective_period = _FINANCIAL_REPORT_PERIOD_MAP.get(period, period) if period else self.period
        primary_reports = self._get_report(period=effective_period, lang=lang, show_log=show_log)[0]
        
        balance_sheet_df = primary_reports[report_key]
        if dropna:
            # fill NaN values with 0
            balance_sheet_df = balance_sheet_df.fillna(0)
            # drop columns with all 0 values
            balance_sheet_df = balance_sheet_df.loc[:, (balance_sheet_df != 0).any(axis=0)]

        if effective_period == 'Y':
            if lang == 'en':
                balance_sheet_df = balance_sheet_df.drop(columns='lengthReport')
            elif lang == 'vi':
                balance_sheet_df = balance_sheet_df.drop(columns='Kỳ')
        return balance_sheet_df
    
    def balance_sheet(self, period:Optional[str]=None, lang:Optional[str]='en', dropna:Optional[bool]=False, show_log:Optional[bool]=False):
        return self._process_report('Chỉ tiêu cân đối kế toán', period=period, lang=lang, dropna=dropna, show_log=show_log)
    
    def income_statement(self, period:Optional[str]=None, lang:Optional[str]='en', dropna:Optional[bool]=False, show_log:Optional[bool]=False):
        return self._process_report('Chỉ tiêu kết quả kinh doanh', period=period, lang=lang, dropna=dropna, show_log=show_log)
    
    def cash_flow(self, period:Optional[str]=None, lang:Optional[str]='en', dropna:Optional[bool]=False, show_log:Optional[bool]=False):
        return self._process_report('Chỉ tiêu lưu chuyển tiền tệ', period=period, lang=lang, dropna=dropna, show_log=show_log)
 
    def ratio(self, period:Optional[str]=None, lang:Optional[str]='en', dropna:Optional[bool]=True, show_log:Optional[bool]=False):
        effective_period = _FINANCIAL_REPORT_PERIOD_MAP.get(period, period) if period else self.period
        financial_report = self._get_report(period=effective_period, lang=lang, show_log=show_log)[1]

        # if effective_period == 'Y':
        #     if lang == 'en':
        #         financial_report = financial_report.drop(columns='lengthReport')
        #     elif lang == 'vi':
        #         financial_report = financial_report.drop(columns='Kỳ')
        return financial_report