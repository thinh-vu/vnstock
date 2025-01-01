import json
import requests
import pandas as pd
from typing import Optional, List, Dict
from .const import _GRAPHQL_URL, _FINANCIAL_REPORT_PERIOD_MAP, _UNIT_MAP, _ICB4_COMTYPE_CODE_MAP, SUPPORTED_LANGUAGES
from vnstock.explorer.vci import Company
from vnstock.core.utils.parser import get_asset_type, camel_to_snake, api_response_check
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers

logger = get_logger(__name__)

class Finance ():
    """
    Truy xuất thông tin báo cáo tài chính của một công ty theo mã chứng khoán từ nguồn dữ liệu VCI.

    Tham số:
        - symbol (str): Mã chứng khoán của công ty cần truy xuất thông tin.
        - period (str): Chu kỳ báo cáo tài chính cần truy xuất. Mặc định là 'quarterly'.
    """

    def __init__(self, symbol, period:Optional[str]='quarter', get_all:Optional[bool]=True, show_log:Optional[bool]=True):
        self.symbol = symbol.upper()
        self.asset_type = get_asset_type(self.symbol)
        self.headers = get_headers(data_source='VCI')
        self.show_log = show_log

        if not show_log:
            logger.setLevel('CRITICAL')

        # validate input for period
        if period not in ['year', 'quarter']:
            raise ValueError("Kỳ báo cáo tài chính không hợp lệ. Chỉ chấp nhận 'year' hoặc 'quarter'.")
        # if asset_type is not stock, raise error
        if self.asset_type not in ['stock']:
            raise ValueError("Mã chứng khoán không hợp lệ. Chỉ cổ phiếu mới có thông tin.")
        self.period = _FINANCIAL_REPORT_PERIOD_MAP.get(period)
        self.get_all = get_all
        self.com_type_code = self._get_company_type()
    
    def _get_company_type(self):
        """
        Get the company type code from ICB4_COMTYPE_CODE_MAP based on the company's ICB4 industry classification for report mapping.

        Returns:
        - str: The company type code. Possible values:
            'CT': Công ty (Company)
            'CK': Chứng khoán (Securities)
            'NH': Ngân hàng (Bank)
            'BH': Bảo hiểm (Insurance)
        """
        # Get the company's ICB4 industry classification
        listing_info = Company(symbol=self.symbol)._fetch_data()['CompanyListingInfo']
        com_type_code = _ICB4_COMTYPE_CODE_MAP[listing_info['icbName4']]
        return com_type_code

    # @staticmethod
    # def handle_duplicate_columns(self, original_columns: List[str], ratio_df: pd.DataFrame) -> pd.DataFrame:
    #     """
    #     Handles duplicate column names in a DataFrame by appending the original column name
    #     as a suffix to the duplicate column names.

    #     Parameters:
    #     - original_columns (List[str]): A list of the original column names before renaming.
    #     - ratio_df (pd.DataFrame): The DataFrame with potentially duplicated column names after renaming.

    #     Returns:
    #     - pd.DataFrame: The DataFrame with resolved column names.
    #     """
    #     seen_columns = {}
    #     renamed_columns = []

    #     for i, col in enumerate(ratio_df.columns):
    #         original_col = original_columns[i]
    #         if col in seen_columns:
    #             # If duplicate, append the original column name as a suffix
    #             new_col_name = f"{col} - {original_col}"
    #             renamed_columns.append(new_col_name)
    #         else:
    #             seen_columns[col] = 1
    #             renamed_columns.append(col)

    #     # Apply the new column names to the DataFrame
    #     ratio_df.columns = renamed_columns
        
    #     return ratio_df
    
    @staticmethod
    def duplicated_columns_handling (all_columns_mapping, target_col_name='name'):
        """
        Handles duplicate column names in a DataFrame by appending the original column name
        as a suffix to the duplicate column names.

        Parameters:
        - all_columns_mapping (pd.DataFrame): The DataFrame with potentially duplicated column names after renaming.
        - target_col_name (str): The column name to check for duplicates. Default is 'name', other possible values are 'en_name'.

        Returns:
        - pd.DataFrame: The DataFrame with resolved column names.
        """
        # duplicated subset
        duplicated_subset = all_columns_mapping[all_columns_mapping[target_col_name].duplicated()].copy()
        # non-duplicated subset
        non_duplicated_subset = all_columns_mapping[~all_columns_mapping[target_col_name].duplicated()].copy()
        # replace values the duplicated columns by appending the field_name
        duplicated_subset[target_col_name] = all_columns_mapping['name'] + ' - ' + all_columns_mapping['field_name']
        # combine the two subsets
        all_columns_mapping = pd.concat([non_duplicated_subset, duplicated_subset])
        return all_columns_mapping
    
    # @staticmethod
    def _get_ratio_dict(self, show_log:Optional[bool]=False, get_all:Optional[bool]=False):
        """
        Get the dictionary mapping for all financial metrics from VCI source.

        Parameters:
            - show_log (bool): Whether to show log messages. Default is False.
            - get_all (bool): Whether to get all columns. Default is False.
        Returns:
            - pd.DataFrame: A DataFrame containing the mapping between 'field_name', 'name', 'en_name', 'type', 'order', 'unit
        """
        payload = "{\"query\":\"query Query {\\n  ListFinancialRatio {\\n    id\\n    type\\n    name\\n    unit\\n    isDefault\\n    fieldName\\n    en_Type\\n    en_Name\\n    tagName\\n    comTypeCode\\n    order\\n    __typename\\n  }\\n}\\n\",\"variables\":{}}"
        if show_log:
            logger.debug(f"Requesting financial ratio data from {_GRAPHQL_URL}. payload: {payload}")
        response = requests.request("POST", _GRAPHQL_URL, headers=self.headers, data=payload)
        if response.status_code != 200:
            logger.error(f"Request failed with status code {response.status_code}. Details: {response.text}")
        data = response.json()['data']['ListFinancialRatio']
        df = pd.DataFrame(data)
        df.columns = [camel_to_snake(col).replace('__', '_') for col in df.columns]
        effective_get_all = get_all if get_all is not None else self.get_all
        selected_columns = ['field_name', 'name', 'en_name', 'type', 'order', 'unit', 'com_type_code']
        df['unit'] = df['unit'].map(_UNIT_MAP)
        if effective_get_all is False:
            df = df[selected_columns]
        df.columns = [col.replace('__', '_') for col in df.columns]
        return df

    def _get_report (self, period:Optional[str]=None, lang:Optional[str]='en', show_log:Optional[bool]=False, mode:Optional[str]='final'):
        """
        Get the financial report data for a company from VCI source.
        
        Parameters:
            - period (str): The period of the financial report. Default is None.
            - lang (str): The language of the report. Default is 'en'.
            - show_log (bool): Whether to show log messages. Default is False.
            - mode (str): The mode of the report. Default is 'final' which return polish data after the mapping process. Other mode is 'raw' which return the raw data which contains code names for all fields.
        """
        # if lange not in SUPPORTED_LANGUAGES then raise error
        if lang not in SUPPORTED_LANGUAGES:
            supported_languages_str = ", ".join(SUPPORTED_LANGUAGES)
            raise ValueError(f"Invalid language specified: '{lang}'. Supported languages are: {supported_languages_str}.")
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

        data = api_response_check(response)
        selected_data = data['data']['CompanyFinancialRatio']['ratio']
        ratio_df = pd.DataFrame(selected_data)
        if mode == 'final':
            primary_dfs, other_reports = self._ratio_mapping(ratio_df, lang=lang, show_log=show_log)
            return primary_dfs, other_reports
        elif mode == 'raw':
            return ratio_df
        
    def _ratio_mapping (self, ratio_df:pd.DataFrame, lang:Optional[str]='en', mode:str='final', show_log:Optional[bool]=False):
        """
        A dedicated method to map the financial ratio DataFrame to different reports based on the company type code.

        Parameters:
            - ratio_df (pd.DataFrame): The DataFrame containing the financial ratio from the function _get_report().
            - lang (str): The language of the report. Default is 'en'.
            - mode (str): The mode of the report. Default is 'final' which return polish data after the mapping process & translation. Other mode is 'raw' which return the raw data which contains code names for all fields.
            - show_log (bool): Whether to show log messages. Default is False.

        Returns:
            - pd.DataFrame: A DataFrame containing the financial ratio data.

        Attributes: (only available when show_log is True)
            - type_field_dict (dict): A dictionary mapping the report type to the list of field names.
            - raw_ratio_df (pd.DataFrame): The raw DataFrame containing the financial ratio data with code name columns such as isa, isb, etc.
        """

        if lang == 'vi':
            ratio_df = ratio_df.rename(columns={'ticker': 'CP', 'yearReport': 'Năm', 'lengthReport': 'Kỳ'})
            index_cols = ['CP', 'Năm', 'Kỳ']
            index_part = ratio_df[index_cols]
            target_col_name = 'name'
        elif lang == 'en':
            index_cols = ['ticker', 'yearReport', 'lengthReport']
            index_part = ratio_df[index_cols]
            target_col_name = 'en_name'

        # Create a dictionary to map field_name to report type
        mapping_df = self._get_ratio_dict(get_all=False)
        # Filter the mapping DataFrame based on company type code. Split mapping into two parts: 'CT' and company-specific mapping
        if self.com_type_code != 'CT':
            mapping_specific = mapping_df[mapping_df['com_type_code'] == self.com_type_code]
        else:
            mapping_specific = pd.DataFrame()
        mapping_ct = mapping_df[mapping_df['com_type_code'] == 'CT']
        all_columns_mapping = pd.concat([mapping_specific, mapping_ct]).drop_duplicates(subset='field_name', keep='first')

        # remove all values that com_type_code is not 'CT' or self.com_type_code
        all_columns_mapping = all_columns_mapping[all_columns_mapping['com_type_code'].isin(['CT', self.com_type_code])].copy()

        original_columns = ratio_df.columns
        # There are many columns in ratio_df that are not in mapping_df, they are not tied to the company specific mapping or the 'CT' mapping
        orphan_columns = [col for col in original_columns if col not in mapping_df['field_name'].values and col not in index_part.columns]
        if show_log:
            logger.debug(f"Orphan columns will be dropped: {orphan_columns}")

        columns_translation = all_columns_mapping.set_index('field_name')[target_col_name].to_dict()
        # Create a dictionary to map field_name to order
        column_order = all_columns_mapping.set_index(target_col_name)['order'].to_dict()
         
        # Drop the orphan columns which are not in the mapping DataFrame
        ratio_df = ratio_df.drop(columns=orphan_columns)
        # apply sorting to the columns of ratio_df by the order in the column_order dictionary
        ratio_df = ratio_df[sorted(ratio_df.columns, key=lambda x: column_order.get(x, 0))]    
        type_field_dict = all_columns_mapping.groupby('type')['field_name'].apply(list).to_dict()

        # Assign attributes to the class in the case of debugging
        self.raw_ratio_df = ratio_df.copy()
        self.columns_mapping = columns_translation

        # Create DataFrames for each report type, using columns name as code names without translation
        report_dfs = {}
        for report_type, fields in type_field_dict.items():
            report_dfs[report_type] = ratio_df[fields]

        # Define the primary report types
        primary_reports = [
            'Chỉ tiêu cân đối kế toán',
            'Chỉ tiêu lưu chuyển tiền tệ',
            'Chỉ tiêu kết quả kinh doanh'
        ]

        # Splitting the reports
        primary_dfs = {key: report_dfs[key] for key in primary_reports}
        other_reports = {key: report_dfs[key] for key in report_dfs if key not in primary_reports}


        # Create a dictionary to map field_name to report type
        name_mapping = dict(zip(mapping_df['field_name'], mapping_df[target_col_name]))

        # Translate the column names
        for key in primary_dfs:
            primary_dfs[key].columns = [name_mapping.get(col, col) for col in primary_dfs[key].columns]

        for key in other_reports:
            other_reports[key].columns = [name_mapping.get(col, col) for col in other_reports[key].columns]

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
                [multi_level_columns_translate(col, columns_translation) for col in merged_other_reports.columns]
            )

        return primary_dfs, merged_other_reports

    def _process_report (self, report_key:str , period:Optional[str]=None, lang:Optional[str]='en', dropna:Optional[bool]=False, show_log:Optional[bool]=False):
        """
        Process the financial report data for a company from VCI source from a single downloaded data in _get_report method.

        Parameters:
            - report_key (str): The key of the report to be processed. Must be one of 'Chỉ tiêu kết quả kinh doanh', 'Chỉ tiêu cân đối kế toán', 'Chỉ tiêu lưu chuyển tiền tệ'.
            - period (str): The period of the financial report. Default is None.
            - lang (str): The language of the report. Default is 'en'.
            - dropna (bool): Whether to drop columns with all 0 values. Default is True.
            - show_log (bool): Whether to show log messages. Default is False.
        """
        # validate report_key should be in 'Chỉ tiêu kết quả kinh doanh', 'Chỉ tiêu cân đối kế toán', 'Chỉ tiêu lưu chuyển tiền tệ'
        if report_key not in ['Chỉ tiêu kết quả kinh doanh', 'Chỉ tiêu cân đối kế toán', 'Chỉ tiêu lưu chuyển tiền tệ']:
            raise ValueError("Báo cáo không hợp lệ. Chỉ chấp nhận 'Chỉ tiêu kết quả kinh doanh', 'Chỉ tiêu cân đối kế toán', 'Chỉ tiêu lưu chuyển tiền tệ'.")

        effective_period = _FINANCIAL_REPORT_PERIOD_MAP.get(period, period) if period else self.period
        primary_reports = self._get_report(period=effective_period, lang=lang, show_log=show_log)[0]

        target_report_df = primary_reports[report_key]
        if dropna:
            # fill NaN values with 0
            target_report_df = target_report_df.fillna(0)
            # drop columns with all 0 values
            target_report_df = target_report_df.loc[:, (target_report_df != 0).any(axis=0)]

        if effective_period == 'Y':
            if lang == 'en':
                target_report_df = target_report_df.drop(columns='lengthReport')
            elif lang == 'vi':
                target_report_df = target_report_df.drop(columns='Kỳ')
        return target_report_df

    def balance_sheet(self, period:Optional[str]=None, lang:Optional[str]='en', dropna:Optional[bool]=True, show_log:Optional[bool]=False):
        """
        Extract the balance sheet data for a company from VCI source.

        Parameters:
            - period (str): The period of the financial report. Default is None.
            - lang (str): The language of the report. Default is 'en'.
            - dropna (bool): Whether to drop columns with all 0 values. Default is True.
            - show_log (bool): Whether to show log messages. Default is False.
        Returns:
            - pd.DataFrame: A DataFrame containing the balance sheet data.
        """
        return self._process_report('Chỉ tiêu cân đối kế toán', period=period, lang=lang, dropna=dropna, show_log=show_log)

    def income_statement(self, period:Optional[str]=None, lang:Optional[str]='en', dropna:Optional[bool]=True, show_log:Optional[bool]=False):
        """
        Extract the income statement data for a company from VCI source.
        
        Parameters:
            - period (str): The period of the financial report. Default is None.
            - lang (str): The language of the report. Default is 'en'.
            - dropna (bool): Whether to drop columns with all 0 values. Default is True.
            - show_log (bool): Whether to show log messages. Default is False.
        Returns:
            - pd.DataFrame: A DataFrame containing the income statement data.
        """
        return self._process_report('Chỉ tiêu kết quả kinh doanh', period=period, lang=lang, dropna=dropna, show_log=show_log)

    def cash_flow(self, period:Optional[str]=None, lang:Optional[str]='en', dropna:Optional[bool]=True, show_log:Optional[bool]=False):
        """
        Extract the cash flow data for a company from VCI source.
        
        Parameters:
            - period (str): The period of the financial report. Default is None.
            - lang (str): The language of the report. Default is 'en'.
            - dropna (bool): Whether to drop columns with all 0 values. Default is True.
            - show_log (bool): Whether to show log messages. Default is False.
        Returns:
            - pd.DataFrame: A DataFrame containing the cash flow data.
        """
        return self._process_report('Chỉ tiêu lưu chuyển tiền tệ', period=period, lang=lang, dropna=dropna, show_log=show_log)

    def ratio(self, period:Optional[str]=None, lang:Optional[str]='en', dropna:Optional[bool]=True, show_log:Optional[bool]=False):
        """
        Extract the financial ratio data for a company from VCI source.

        Parameters:
            - period (str): The period of the financial report. Default is None.
            - lang (str): The language of the report. Default is 'en'.
            - dropna (bool): Whether to drop columns with all 0 values. Default is True.
            - show_log (bool): Whether to show log messages. Default is False.
        """
        effective_period = _FINANCIAL_REPORT_PERIOD_MAP.get(period, period) if period else self.period
        financial_report = self._get_report(period=effective_period, lang=lang, show_log=show_log)[1]
        if dropna:
            # fill NaN values with 0
            financial_report = financial_report.fillna(0)
            # drop columns with all 0 values
            financial_report = financial_report.loc[:, (financial_report != 0).any(axis=0)]

        # if effective_period == 'Y':
        #     if lang == 'en':
        #         financial_report = financial_report.drop(columns='lengthReport')
        #     elif lang == 'vi':
        #         financial_report = financial_report.drop(columns='Kỳ')
        return financial_report
