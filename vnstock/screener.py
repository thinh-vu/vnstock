from .stock import *

## STOCK COMPARISON

def industry_analysis (symbol, lang='vi'):
    """
    This function returns an overview of rating for companies at the same industry with the desired stock symbol.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
        lang (:obj:`str`, optional): 'vi' for Vietnamese, 'en' for English. Default is 'vi'.
    """
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/rating/detail/council?tickers={}&fType=INDUSTRIES'.format(symbol)).json()
    df = json_normalize(data)
    data1 = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/rating/detail/single?ticker={}&fType=TICKER'.format(symbol)).json()
    df1 = json_normalize(data1)
    df = pd.concat([df1, df]).reset_index(drop=True)
    # if label=vi, then rename all columns: ticker to Mã CP, marcap to Vốn hóa (tỷ), price to Giá, numberOfDays to Số phiên tăng/giảm liên tiếp, priceToEarning to P/E, peg to PEG, priceToBook to P/B, dividend to Cổ tức, roe to ROE, roa to ROA, ebitOnInterest to Thanh toán lãi vay, currentPayment to Thanh toán hiện hành, quickPayment to Thanh toán nhanh, grossProfitMargin to Biên LNG, postTaxMargin to Biên LNST, debtOnEquity to Nợ/Vốn CSH, debtOnEbitda to Nợ/EBITDA, income5year to LNST 5 năm,  sale5year to Doanh thu 5 năm, income1quarter to LNST quý gần nhất, sale1quarter to Doanh thu quý gần nhất, nextIncome to LNST năm tới, nextSale to Doanh thu quý tới, rsi to RSI
    # drop na columns
    df = df.dropna(axis=1, how='all')
    if lang == 'vi':
        column_names = {'ticker': 'Mã CP', 'marcap': 'Vốn hóa (tỷ)', 'price': 'Giá', 'numberOfDays': 'Số phiên tăng/giảm liên tiếp', 'priceToEarning': 'P/E', 'peg': 'PEG', 'priceToBook': 'P/B', 'valueBeforeEbitda':'EV/EBITDA', 'dividend': 'Cổ tức', 'roe': 'ROE', 'roa': 'ROA', 'badDebtPercentage' : ' Tỉ lệ nợ xấu', 'ebitOnInterest': 'Thanh toán lãi vay', 'currentPayment': 'Thanh toán hiện hành', 'quickPayment': 'Thanh toán nhanh', 'grossProfitMargin': 'Biên LNG', 'postTaxMargin': 'Biên LNST', 'debtOnEquity': 'Nợ/Vốn CSH', 'debtOnEbitda': 'Nợ/EBITDA', 'income5year': 'LNST 5 năm',  'sale5year':  'Doanh thu 5 năm',  'income1quarter':  'LNST quý gần nhất',  'sale1quarter':  'Doanh thu quý gần nhất',  'nextIncome':  'LNST năm tới',  'nextSale':  'Doanh thu năm tới',  "rsi": "RSI"}
        df.rename(columns=column_names, inplace=True)
    elif lang == 'en':
        pass
    # transpose dataframe
    df = df.T
    # set ticker row as column name then drop ticker row
    df.columns = df.iloc[0]
    df = df.drop(df.index[0])
    return df

def stock_ls_analysis (symbol_ls, lang='vi'):
    """
    This function returns an overview of rating for a list of companies by entering list of stock symbols.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
        lang (:obj:`str`, optional): Set to 'vi' to retrieve the column labels in Vietnamese, 'en' to retrieve the data in English. Default is 'vi'.
    """
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/rating/detail/council?tickers={}&fType=TICKERS'.format(symbol_ls)).json()
    df = json_normalize(data).dropna(axis=1)
    # if label=vi, then rename all columns: ticker to Mã CP, marcap to Vốn hóa (tỷ), price to Giá, numberOfDays to Số phiên tăng/giảm liên tiếp, priceToEarning to P/E, peg to PEG, priceToBook to P/B, dividend to Cổ tức, roe to ROE, roa to ROA, ebitOnInterest to Thanh toán lãi vay, currentPayment to Thanh toán hiện hành, quickPayment to Thanh toán nhanh, grossProfitMargin to Biên LNG, postTaxMargin to Biên LNST, debtOnEquity to Nợ/Vốn CSH, debtOnEbitda to Nợ/EBITDA, income5year to LNST 5 năm,  sale5year to Doanh thu 5 năm, income1quarter to LNST quý gần nhất, sale1quarter to Doanh thu quý gần nhất, nextIncome to LNST năm tới, nextSale to Doanh thu quý tới, rsi to RSI
    # drop na columns
    df = df.dropna(axis=1, how='all')
    if lang == 'vi':
        column_names = {'ticker': 'Mã CP', 'marcap': 'Vốn hóa (tỷ)', 'price': 'Giá', 'numberOfDays': 'Số phiên tăng/giảm liên tiếp', 'priceToEarning': 'P/E', 'peg': 'PEG', 'priceToBook': 'P/B', 'valueBeforeEbitda':'EV/EBITDA', 'dividend': 'Cổ tức', 'roe': 'ROE', 'roa': 'ROA', 'badDebtPercentage' : ' Tỉ lệ nợ xấu', 'ebitOnInterest': 'Thanh toán lãi vay', 'currentPayment': 'Thanh toán hiện hành', 'quickPayment': 'Thanh toán nhanh', 'grossProfitMargin': 'Biên LNG', 'postTaxMargin': 'Biên LNST', 'debtOnEquity': 'Nợ/Vốn CSH', 'debtOnEbitda': 'Nợ/EBITDA', 'income5year': 'LNST 5 năm',  'sale5year':  'Doanh thu 5 năm',  'income1quarter':  'LNST quý gần nhất',  'sale1quarter':  'Doanh thu quý gần nhất',  'nextIncome':  'LNST năm tới',  'nextSale':  'Doanh thu năm tới',  "rsi": "RSI", "rs":"RS"}
        df.rename(columns=column_names, inplace=True)
    elif lang == 'en':
        pass
    # transpose dataframe
    df = df.T
    # set ticker row as column name then drop ticker row
    df.columns = df.iloc[0]
    df = df.drop(df.index[0])
    return df


# -----------------------------------------------------------------
# STOCK SCREENER


def stock_screening_insights (params, size=50, id=None, drop_lang='vi', headers=tcbs_headers):
    """
    Get stock screening insights from TCBS Stock Screener
    Parameters:
        params (dict): a dictionary of parameters and their values for the stock screening. The keys should be the names of the filters, and the values should be either a single value or a tuple of two values (min and max) for the filter. For example:
            params = {
                "exchangeName": "HOSE,HNX,UPCOM",
                "epsGrowth1Year": (0, 1000000)
            }
        size (int): number of data points per page. Default is 50. You can increase this parameter to about 1700 to get all data in one trading day.
        id (str): ID of the stock screener. You can ignore this parameter.
        drop_lang (str): language of the column names to drop. Default is 'vi'.
        headers (dict): headers of the request. You can ignore this parameter.
    """
    url = "https://apipubaws.tcbs.com.vn/ligo/v1/watchlist/preview"
    # create a list of filters based on the params dictionary
    filters = []
    for key, value in params.items():
        # if the value is a tuple, it means it has a min and max value
        if isinstance(value, tuple):
            min_value, max_value = value
            filters.append({
                "key": key,
                "operator": ">=",
                "value": min_value
            })
            filters.append({
                "key": key,
                "operator": "<=",
                "value": max_value
            })
        # otherwise, it is a single value
        else:
            filters.append({
                "key": key,
                "value": value,
                "operator": "="
            })
    payload = json.dumps({
        "tcbsID": id,
        "filters": filters,
        "size": params.get("size", size) # use a default value for size if not specified
    })
    # send request to get response
    response = requests.request("POST", url, headers=headers, data=payload).json()
    df = json_normalize(response['searchData']['pageContent'])
    # drop all columns has column name ended with `.vi`
    df = df[df.columns.drop(list(df.filter(regex=f'\.{drop_lang}$')))]
    # drop na columns
    df = df.dropna(axis=1, how='all')
    return df
