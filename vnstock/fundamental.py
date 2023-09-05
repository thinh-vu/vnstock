from .config import *

# FINANCIAL REPORT
def financial_report (symbol, report_type, frequency, headers=ssi_headers): # Quarterly, Yearly
    """
    This function returns the balance sheet of a stock symbol by a Quarterly or Yearly range.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
        report_type (:obj:`str`, required): BalanceSheet, IncomeStatement, CashFlow
        report_range (:obj:`str`, required): Yearly or Quarterly.
    """
    url = 'https://fiin-fundamental.ssi.com.vn/FinancialStatement/Download{}?language=vi&OrganCode={}&Skip=0&Frequency={}'.format(report_type, symbol, frequency)
    r = requests.get(url, headers=headers)
    df = pd.read_excel(BytesIO(r.content), skiprows=7).dropna()
    return df

def financial_ratio_compare (symbol_ls, industry_comparison, frequency, start_year, headers=ssi_headers): 
    """
    This function returns the balance sheet of a stock symbol by a Quarterly or Yearly range.
    Args:
        symbol (:obj:`str`, required): ["CTG", "TCB", "ACB"].
        industry_comparison (:obj: `str`, required): "true" or "false"
        report_range (:obj:`str`, required): Yearly or Quarterly.
    """
    global timeline
    if frequency == 'Yearly':
      timeline = str(start_year) + '_5'
    elif frequency == 'Quarterly':
      timeline = str(start_year) + '_4'

    for i in range(len(symbol_ls)):
      if i == 0:
        company_join = '&CompareToCompanies={}'.format(symbol_ls[i])
        url = 'https://fiin-fundamental.ssi.com.vn/FinancialAnalysis/DownloadFinancialRatio2?language=vi&OrganCode={}&CompareToIndustry={}{}&Frequency={}&Ratios=ryd21&Ratios=ryd25&Ratios=ryd14&Ratios=ryd7&Ratios=rev&Ratios=isa22&Ratios=ryq44&Ratios=ryq14&Ratios=ryq12&Ratios=rtq51&Ratios=rtq50&Ratios=ryq48&Ratios=ryq47&Ratios=ryq45&Ratios=ryq46&Ratios=ryq54&Ratios=ryq55&Ratios=ryq56&Ratios=ryq57&Ratios=nob151&Ratios=casa&Ratios=ryq58&Ratios=ryq59&Ratios=ryq60&Ratios=ryq61&Ratios=ryd11&Ratios=ryd3&TimeLineFrom={}'.format(symbol_ls[i], industry_comparison, '', frequency, timeline)
      elif i > 0:
        company_join = '&'.join([company_join, 'CompareToCompanies={}'.format(symbol_ls[i])])
        url = 'https://fiin-fundamental.ssi.com.vn/FinancialAnalysis/DownloadFinancialRatio2?language=vi&OrganCode={}&CompareToIndustry={}{}&Frequency={}&Ratios=ryd21&Ratios=ryd25&Ratios=ryd14&Ratios=ryd7&Ratios=rev&Ratios=isa22&Ratios=ryq44&Ratios=ryq14&Ratios=ryq12&Ratios=rtq51&Ratios=rtq50&Ratios=ryq48&Ratios=ryq47&Ratios=ryq45&Ratios=ryq46&Ratios=ryq54&Ratios=ryq55&Ratios=ryq56&Ratios=ryq57&Ratios=nob151&Ratios=casa&Ratios=ryq58&Ratios=ryq59&Ratios=ryq60&Ratios=ryq61&Ratios=ryd11&Ratios=ryd3&TimeLineFrom=2017_5'.format(symbol_ls[i], industry_comparison, company_join, frequency, timeline)
    r = requests.get(url, headers=headers)
    df = pd.read_excel(BytesIO(r.content), skiprows=7)
    return df


# STOCK FILTERING

def financial_ratio (symbol, report_range, is_all=False):
    """
    This function retrieves the essential financial ratios of a stock symbol on a quarterly or yearly basis. Some of the expected ratios include: P/E, P/B, ROE, ROA, BVPS, etc
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
        report_range (:obj:`str`, required): 'yearly' or 'quarterly'.
        is_all (:obj:`boo`, required): Set to True to retrieve all available years of data,  False to retrieve the last 5 years data (or the last 10 quarters). Default is True.
    """
    if report_range == 'yearly':
        x = 1
    elif report_range == 'quarterly':
        x = 0
    
    if is_all == True:
      y = 'true'
    else:
      y = 'false'

    data = requests.get(f'https://apipubaws.tcbs.com.vn/tcanalysis/v1/finance/{symbol}/financialratio?yearly={x}&isAll={y}').json()
    df = json_normalize(data)
    # drop nan columns
    df = df.dropna(axis=1, how='all')
    #if report_range == 'yearly' then set index column to be df['year'] and drop quarter column, else set index to df['year'] + df['quarter']
    if report_range == 'yearly':
        df = df.set_index('year').drop(columns={'quarter'})
    elif report_range == 'quarterly':
        # add prefix 'Q' to quarter column
        df['quarter'] = 'Q' + df['quarter'].astype(str)
        # concatenate quarter and year columns
        df['range'] = df['quarter'].str.cat(df['year'].astype(str), sep='-')
        # move range column to the first column
        df = df[['range'] + [col for col in df.columns if col != 'range']]
        # set range column as index
        df = df.set_index('range')
    df = df.T
    return df

def financial_flow(symbol='TCB', report_type='incomestatement', report_range='quarterly', get_all=True): # incomestatement, balancesheet, cashflow | report_range: 0 for quarterly, 1 for yearly
    """
    This function returns the quarterly financial ratios of a stock symbol. Some of expected ratios are: priceToEarning, priceToBook, roe, roa, bookValuePerShare, etc
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
        report_type (:obj:`str`, required): select one of 3 reports: incomestatement, balancesheet, cashflow.
        report_range (:obj:`str`, required): yearly or quarterly.
    """
    if report_range == 'yearly':
        range = 1
    elif report_range == 'quarterly':
        range = 0
    data = requests.get(f'https://apipubaws.tcbs.com.vn/tcanalysis/v1/finance/{symbol}/{report_type}', params={'yearly': range, 'isAll': get_all}).json()
    df = json_normalize(data)
    df[['year', 'quarter']] = df[['year', 'quarter']].astype(str)
    # if report_range == 'yearly' then set index to df['year'], else set index to df['year'] + df['quarter']
    if report_range == 'yearly':
        df['index'] = df['year']
    elif report_range == 'quarterly':
        df['index'] = df['year'].str.cat('-Q' + df['quarter'])
    df = df.set_index('index').drop(columns={'year', 'quarter'})
    return df

def dividend_history (symbol):
    """
    This function returns the dividend historical data of the seed stock symbol.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
    """
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/company/{}/dividend-payment-histories?page=0&size=20'.format(symbol)).json()
    df = json_normalize(data['listDividendPaymentHis']).drop(columns=['no', 'ticker'])
    return df


## STOCK RATING
def  general_rating (symbol):
    """
    This function returns a dataframe with all rating aspects for the desired stock symbol.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
    """
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/rating/{}/general?fType=TICKER'.format(symbol)).json()
    df = json_normalize(data).drop(columns='stockRecommend')
    return df

def biz_model_rating (symbol):
    """
    This function returns the business model rating for the desired stock symbol.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
    """
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/rating/{}/business-model?fType=TICKER'.format(symbol)).json()
    df = json_normalize(data)
    return df

def biz_operation_rating (symbol):
    """
    This function returns the business operation rating for the desired stock symbol.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
    """
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/rating/{}/business-operation?fType=TICKER'.format(symbol)).json()
    df = json_normalize(data)
    return df

def financial_health_rating (symbol):
    """
    This function returns the financial health rating for the desired stock symbol.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
    """
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/rating/{}/financial-health?fType=TICKER'.format(symbol)).json()
    df = json_normalize(data)
    return df


def valuation_rating (symbol):
    """
    This function returns the valuation rating for the desired stock symbol.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
    """
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/rating/{}/valuation?fType=TICKER'.format(symbol)).json()
    df = json_normalize(data)
    return df


def industry_financial_health (symbol):
    """
    This function returns the industry financial health rating for the seed stock symbol.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
    """
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/rating/{}/financial-health?fType=INDUSTRY'.format(symbol)).json()
    df = json_normalize(data)
    return df


# RECENTLY ADDED -------

def stock_evaluation (symbol='ACB', period=1, time_window='D', headers=tcbs_headers):
    """
    Return a DataFrame contains the stock evaluation data of the ticker.
    Parameters:
    symbol (str): ticker of the company, default is 'ACB', other tickers available can be obtained from the function `listing_companies()`.
    period (int): period of the stock evaluation, default is 1. All available: '1' (1 year), '3' (3 years), '5' (5 years)
    time_window (str): time window of the stock evaluation, default is 'D'. All available: 'D' (1 day), 'W' (1 week). For period = 1, time_window = 'D' or 'W', otherwise time_window = 'W'.
    """
    # create url to get stock evaluation data
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/evaluation/{symbol}/historical-chart?period={period}&tWindow={time_window}"
    # get stock evaluation data
    response = requests.get(url, headers=headers).json()
    # convert json to dataframe
    df = pd.DataFrame(response['data'])
    # rename columns: pe to PE, pb to PB, industryPe to Industry PE, industryPb to Industry PB, indexPe to VNIndex PE, indexPb to VNIndex PB
    df.rename(columns={'pe': 'PE', 'pb': 'PB', 'industryPe': 'industryPE', 'industryPb': 'industryPB', 'indexPe': 'vnindexPE', 'indexPb': 'vnindexPB', 'from': 'fromDate', 'to': 'toDate'}, inplace=True)
    # add ticker value to the dataframe
    df['ticker'] = symbol
    # move ticker column to the first column
    df = df[['ticker', 'fromDate', 'toDate', 'PE', 'PB', 'industryPE', 'vnindexPE', 'industryPB', 'vnindexPB']]
    # convert fromDate and toDate to datetime
    df['fromDate'] = pd.to_datetime(df['fromDate'])
    df['toDate'] = pd.to_datetime(df['toDate'])
    return df