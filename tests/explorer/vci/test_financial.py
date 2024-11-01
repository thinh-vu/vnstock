import pytest
import requests
from unittest.mock import patch, Mock
import pandas as pd
from vnstock3.explorer.vci.financial import Finance

# Sample test data and responses
SAMPLE_SYMBOL = "VCI"
INVALID_SYMBOL = "INVALID"
VALID_PERIOD = "quarter"
INVALID_PERIOD = "monthly"
VALID_LANG = "en"
INVALID_LANG = "es"
MOCK_RESPONSE_SUCCESS = {
    "data": {
        "CompanyFinancialRatio": {
            "ratio": [
                {
                    "ticker": "VCI",
                    "yearReport": 2024,
                    "lengthReport": 2,
                    "updateDate": 1723720470520,
                    "revenue": 915851554761,
                    "revenueGrowth": 0.8285294983832435,
                    "netProfit": 279206679897,
                    "netProfitGrowth": 1.3884923400448321,
                    "ebitMargin": 0.5703190020388252,
                    "roe": 0.0982906278,
                    "roic": 0.0770835043,
                    "roa": 0.0405568385,
                    "pe": 26.7562409736,
                    "pb": 2.3702445783,
                    "eps": 486.02526264232523,
                    "currentRatio": 1.6922135652,
                    "cashRatio": 0.3611365994,
                    "quickRatio": 1.6922135652,
                    "interestCoverage": -2.7628770892994985,
                    "ae": 2.608265404033926,
                    "netProfitMargin": 0.3048601909835285,
                    "grossMargin": 0.6076481496831961,
                    "ev": 20996859494000,
                    "issueShare": 574469480,
                    "ps": 6.5727089573,
                    "pcf": -4.9553190578,
                    "bvps": 15420.3495852956,
                    "evPerEbitda": 17.8983507339,
                    "BSA1": 23009916452730,
                    "BSA2": 3903157759657,
                    "BSA5": 17775135464006,
                    "BSA8": 931122579216,
                    "BSA10": 1144858551,
                    "BSA159": 0,
                    "BSA16": 0,
                    "BSA22": 372374861200,
                    "BSA23": 95455335905,
                    "BSA24": 0,
                    "BSA162": 0,
                    "BSA27": 0,
                    "BSA29": 32024143832,
                    "BSA43": 0,
                    "BSA46": 0,
                    "BSA50": 8879984392,
                    "BSA209": 0,
                    "BSA53": 23105371788635,
                    "BSA54": 14246851580952,
                    "BSA55": 13597525115321,
                    "BSA56": 12392104000000,
                    "BSA58": 1753351687,
                    "BSA67": 649326465631,
                    "BSA71": 0,
                    "BSA173": 0,
                    "BSA78": 8858520207683,
                    "BSA79": 8858520207683,
                    "BSA80": 4419000000000,
                    "BSA175": 4419000000000,
                    "BSA86": 0,
                    "BSA90": 1784460323370,
                    "BSA96": 23105371788635,
                    "CFA21": 0,
                    "CFA22": 0,
                    "at": 0.1663347355,
                    "fat": 129.5286323278,
                    "acp": "null",
                    "dso": 0,
                    "dpo": 76.7351129739,
                    "ccc": "null",
                    "de": 1.608265404,
                    "le": 1.3988909783,
                    "ebitda": 1647403505089,
                    "ebit": 522327544727,
                    "dividend": 0.0273597811,
                    "RTQ10": 1.608265404,
                    "charterCapitalRatio": 2.004643631519122,
                    "RTQ4": 0,
                    "epsTTM": 1366.0364337454,
                    "charterCapital": 4419000000000,
                    "fae": 0.003615066972949437,
                    "RTQ17": 0,
                    "CFA26": -12703945273,
                    "CFA6": 0,
                    "CFA9": 134650217917,
                    "BSA85": 0,
                    "CFA36": 1040594399692,
                    "BSB98": 0,
                    "BSB101": 0,
                    "BSA89": 0,
                    "CFA34": 2204238269300,
                    "CFA14": -181036532844,
                    "ISB34": 0,
                    "ISB27": 0,
                    "ISA23": 0,
                    "ISS152": 0,
                    "ISA102": 0,
                    "CFA27": 52800000000,
                    "CFA12": -28947341078,
                    "CFA28": 0,
                    "BSA18": 400500649851,
                    "BSB102": 0,
                    "BSB110": 0,
                    "BSB108": 310000000000,
                    "CFA23": 0,
                    "ISB41": 0,
                    "BSB103": 0,
                    "BSA40": 0,
                    "BSB99": 0,
                    "CFA16": 0,
                    "CFA18": 671029035938,
                    "CFA3": 0,
                    "ISB30": 0,
                    "BSA33": 0,
                    "ISB29": 0,
                    "CFS200": -275508242880,
                    "ISA2": 0,
                    "CFA24": 0,
                    "BSB105": 0,
                    "CFA37": 0,
                    "ISS141": 15645475012,
                    "BSA95": 0,
                    "CFA10": 0,
                    "ISA4": -359336052126,
                    "BSA82": 0,
                    "CFA25": 0,
                    "BSB111": 0,
                    "ISI64": 0,
                    "BSB117": 0,
                    "ISA20": 279206679897,
                    "CFA19": -12703945273,
                    "ISA6": 0,
                    "ISA3": 915851554761,
                    "BSB100": 0,
                    "ISB31": 0,
                    "ISB38": 0,
                    "ISB26": 0,
                    "BSA210": 0,
                    "CFA20": 0,
                    "CFA35": 2862563359965,
                    "ISA17": -64821621464,
                    "ISS148": -189052038091,
                    "BSB115": 0,
                    "ISA9": 0,
                    "CFA4": 0,
                    "ISA7": 0,
                    "CFA5": 0,
                    "ISA22": 279206679897,
                    "CFA8": -15155990142,
                    "CFA33": 0,
                    "CFA29": 5196444000000,
                    "BSA30": 25038030423,
                    "BSA84": 2565263355461,
                    "BSA44": 0,
                    "BSB107": 0,
                    "ISB37": 0,
                    "ISA8": 0,
                    "BSB109": 0,
                    "ISA19": -64559441640,
                    "ISB36": 0,
                    "ISA13": -11399791,
                    "ISA1": 915851554761,
                    "BSB121": 0,
                    "ISA14": 2826585413,
                    "BSB112": 0,
                    "ISA21": 0,
                    "ISA10": -34187957908,
                    "CFA11": 0,
                    "ISA12": 2837985204,
                    "BSA15": 0,
                    "BSB104": 0,
                    "BSA92": 0,
                    "BSB106": 0,
                    "BSA94": 0,
                    "ISA18": 262179824,
                    "CFA17": 0,
                    "ISI87": 0,
                    "BSB114": 0,
                    "ISA15": 0,
                    "BSB116": 0,
                    "ISB28": 0,
                    "BSB97": 0,
                    "CFA15": -37710331505,
                    "ISA11": 340939536124,
                    "ISB33": 0,
                    "BSA47": 0,
                    "ISB40": 0,
                    "ISB39": 0,
                    "CFA7": 189052038091,
                    "CFA13": 5230954410,
                    "ISS146": -197033483615,
                    "ISB25": 0,
                    "BSA45": 0,
                    "BSB118": 0,
                    "CFA1": 343766121537,
                    "CFS191": 0,
                    "ISB35": 0,
                    "CFB65": 0,
                    "CFA31": 0,
                    "BSB113": 0,
                    "ISB32": 0,
                    "ISA16": 343766121537,
                    "CFS210": 685938398293,
                    "BSA48": 0,
                    "BSA36": 6986113409,
                    "ISI97": 0,
                    "CFA30": -3043897000000,
                    "CFA2": 2559060545,
                    "CFB80": 0,
                    "CFA38": 3903157759657,
                    "CFA32": -1108730700,
                    "ISA5": 556515502635,
                    "BSA49": 53224683273,
                    "CFB64": 0,
                    "__typename": "CompanyFinancialRatio"
                },
            ],
            "period": [
                "2024-2",
                "2024-1",
                "2023-4",
                "2023-3",
                "2023-2",
                "2023-1",
                "2022-4",
                "2022-3",
                "2022-2",
                "2022-1",
                "2021-4",
                "2021-3",
                "2021-2",
                "2021-1",
                "2020-4",
                "2020-3",
                "2020-2",
                "2020-1",
                "2019-4",
                "2019-3",
                "2019-2",
                "2019-1",
                "2018-4",
                "2018-3",
                "2018-2",
                "2018-1",
                "2017-4",
                "2017-3",
                "2017-2",
                "2017-1",
                "2016-4",
                "2016-3",
                "2016-2",
                "2016-1",
                "2015-4",
                "2015-3",
                "2015-2",
                "2015-1",
                "2014-4",
                "2014-3",
                "2014-2",
                "2014-1",
                "2013-4",
                "2013-3",
                "2013-2",
                "2013-1"
            ],
            "__typename": "CompanyFinancialRatioPeriod"
        }
    }
}

@pytest.fixture
def finance_instance():
    """Fixture to create a Finance instance for tests."""
    return Finance(symbol=SAMPLE_SYMBOL, period=VALID_PERIOD, get_all=True, show_log=False)

# Initialization Tests
def test_finance_init_valid_symbol(finance_instance):
    """Test initialization with a valid symbol."""
    assert finance_instance.symbol == SAMPLE_SYMBOL.upper()
    assert finance_instance.period is not None

def test_finance_init_invalid_period():
    """Test initialization with an invalid period."""
    with pytest.raises(ValueError, match="Kỳ báo cáo tài chính không hợp lệ"):
        Finance(symbol=SAMPLE_SYMBOL, period=INVALID_PERIOD)

# Test API Call and Mocking
@patch("requests.post")
def test_get_report_successful_response(mock_post, finance_instance):
    """Test _get_report method with a successful API response."""
    mock_post.return_value = Mock(status_code=200, json=lambda: MOCK_RESPONSE_SUCCESS)
    df, _ = finance_instance._get_report(period=VALID_PERIOD, lang=VALID_LANG, show_log=False)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

@patch("requests.post")
def test_get_report_failed_response(mock_post, finance_instance):
    """Test _get_report method handling of a failed API response."""
    mock_post.return_value = Mock(status_code=400, text="Bad Request")
    with pytest.raises(Exception):
        finance_instance._get_report(period=VALID_PERIOD, lang=VALID_LANG, show_log=False)

# Method-specific Tests
@patch("vnstock3.explorer.vci.financial.Company._fetch_data")
def test_get_company_type_valid_company(mock_fetch_data, finance_instance):
    """Test _get_company_type method with a valid company symbol."""
    mock_fetch_data.return_value = {"CompanyListingInfo": {"icbName4": "CT"}}
    assert finance_instance._get_company_type() == "CT"

@patch("vnstock3.explorer.vci.financial.Company._fetch_data")
def test_get_company_type_invalid_symbol(mock_fetch_data, finance_instance):
    """Test _get_company_type method with an invalid symbol."""
    mock_fetch_data.return_value = {"CompanyListingInfo": {"icbName4": None}}
    with pytest.raises(KeyError):
        finance_instance._get_company_type()

# Duplicate Column Handling
def test_duplicated_columns_handling(finance_instance):
    """Test handling of duplicated columns in the DataFrame."""
    sample_df = pd.DataFrame({
        'name': ['Revenue', 'Revenue', 'Net Profit'],
        'field_name': ['rev', 'rev', 'net_profit']
    })
    resolved_df = finance_instance.duplicated_columns_handling(sample_df)
    assert resolved_df['name'].iloc[1] == "Revenue - rev"

# Data Extraction Tests
@patch("requests.post")
def test_balance_sheet_extraction(mock_post, finance_instance):
    """Test balance sheet extraction method with mocked data."""
    mock_post.return_value = Mock(status_code=200, json=lambda: MOCK_RESPONSE_SUCCESS)
    df = finance_instance.balance_sheet(period=VALID_PERIOD, lang=VALID_LANG)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

@patch("requests.post")
def test_income_statement_extraction(mock_post, finance_instance):
    """Test income statement extraction method with mocked data."""
    mock_post.return_value = Mock(status_code=200, json=lambda: MOCK_RESPONSE_SUCCESS)
    df = finance_instance.income_statement(period=VALID_PERIOD, lang=VALID_LANG)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

@patch("requests.post")
def test_cash_flow_extraction(mock_post, finance_instance):
    """Test cash flow extraction method with mocked data."""
    mock_post.return_value = Mock(status_code=200, json=lambda: MOCK_RESPONSE_SUCCESS)
    df = finance_instance.cash_flow(period=VALID_PERIOD, lang=VALID_LANG)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

@patch("requests.post")
def test_ratio_extraction(mock_post, finance_instance):
    """Test ratio extraction method with mocked data."""
    mock_post.return_value = Mock(status_code=200, json=lambda: MOCK_RESPONSE_SUCCESS)
    df = finance_instance.ratio(period=VALID_PERIOD, lang=VALID_LANG)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

# Error Handling Tests
def test_invalid_language(finance_instance):
    """Test _get_report method with an invalid language."""
    with pytest.raises(ValueError, match="Invalid language specified"):
        finance_instance._get_report(period=VALID_PERIOD, lang=INVALID_LANG)

def test_process_report_invalid_report_key(finance_instance):
    """Test _process_report method with an invalid report key."""
    with pytest.raises(ValueError, match="Báo cáo không hợp lệ"):
        finance_instance._process_report("Invalid Key")

# Edge Case Tests
@patch("requests.post")
def test_large_dataset_handling(mock_post, finance_instance):
    """Test the module's ability to handle a large dataset."""
    large_response = {"data": {"CompanyFinancialRatio": {"ratio": [{"fieldName": "field_" + str(i), "value": i} for i in range(10000)]}}}
    mock_post.return_value = Mock(status_code=200, json=lambda: large_response)
    df = finance_instance.ratio(period=VALID_PERIOD, lang=VALID_LANG)
    assert isinstance(df, pd.DataFrame)
    assert len(df.columns) > 0
