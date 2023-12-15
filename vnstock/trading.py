from .config import *

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
    data = requests.get(f'https://apipubaws.tcbs.com.vn/tcanalysis/v1/rating/detail/council?tickers={symbol_ls}&fType=TICKERS').json()
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


## TRADING PRICE TABLE
def price_depth (stock_list='VPB,TCB', headers=vps_headers):
    """
    This function returns the trading price board of a target stocks list.
    Args:
      stock_list (:obj:`str`, required): STRING list of symbols separated by "," without any space. Ex: "TCB,SSI,BID"    
    """
    url = f"https://bgapidatafeed.vps.com.vn/getliststockdata/{stock_list}"
    response = requests.request("GET", url, headers=headers, data={}).json()
    df = json_normalize(response)
    # rename column names in the df: sym to Mã CP, c to Giá Trần, f to Giá Sàn, r to Giá tham chiếu, lot to Tổng Khối Lượng, highPrice to Giá cao, lowPrice to Giá thấp, avePrice to Giá TB, lastPrice to Giá khớp lệnh, lastVolume to KL Khớp lệnh, ot to +/- (Khớp lệnh), changePc to % (Khớp lệnh), fBVol to ĐTNN Mua, fSVolume to ĐTNN Bán
    df.rename(columns={'sym': 'Mã CP', 'c': 'Giá Trần', 'f': 'Giá Sàn', 'r': 'Giá tham chiếu', 'lot': 'Tổng Khối Lượng', 'highPrice': 'Giá cao', 'lowPrice': 'Giá thấp', 'avePrice': 'Giá TB', 'lastPrice': 'Giá khớp lệnh', 'lastVolume': 'KL Khớp lệnh', 'ot': '+/- (Khớp lệnh)', 'changePc': '% (Khớp lệnh)', 'fBVol': 'ĐTNN Mua', 'fSVolume': 'ĐTNN Bán', 'fRoom':'ĐTNN Room'}, inplace=True)
    # for columns in the df, g1 to g7, split by '|', the first value is price, the second value is volume
    df['Giá mua 3'] = df['g1'].str.split('|').str[0]
    df['KL mua 3'] = df['g1'].str.split('|').str[1]
    df['Giá mua 2'] = df['g2'].str.split('|').str[0]
    df['KL mua 2'] = df['g2'].str.split('|').str[1]
    df['Giá mua 1'] = df['g3'].str.split('|').str[0]
    df['KL mua 1'] = df['g3'].str.split('|').str[1]
    df['Giá bán 1'] = df['g4'].str.split('|').str[0]
    df['KL bán 1'] = df['g4'].str.split('|').str[1]
    df['Giá bán 2'] = df['g5'].str.split('|').str[0]
    df['KL bán 2'] = df['g5'].str.split('|').str[1]
    df['Giá bán 3'] = df['g6'].str.split('|').str[0]
    df['KL bán 3'] = df['g6'].str.split('|').str[1]
    # drop columns named from g1 to g6
    df.drop(columns=['id', 'mc', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6'], inplace=True)
    # rearrange columns name by this order: Mã CP, Giá tham chiếu, Giá Trần, Giá Sàn, Giá mua 3, KL mua 3, Giá mua 2, KL mua 2, Giá mua 1, KL mua 1, Giá khớp lệnh, KL Khớp lệnh, +/- (Khớp lệnh), % (Khớp lệnh), Giá bán 1, KL bán 1, Giá bán 2, KL bán 2, Giá bán 3, KL bán 3, Tổng Khối Lượng, ĐTNN Mua, ĐTNN Bán
    df = df[['Mã CP', 'Giá tham chiếu', 'Giá Trần', 'Giá Sàn', 'Giá mua 3', 'KL mua 3', 'Giá mua 2', 'KL mua 2', 'Giá mua 1', 'KL mua 1', 'Giá khớp lệnh', 'KL Khớp lệnh', 'Giá bán 1', 'KL bán 1', 'Giá bán 2', 'KL bán 2', 'Giá bán 3', 'KL bán 3', 'Tổng Khối Lượng', 'ĐTNN Mua', 'ĐTNN Bán', 'ĐTNN Room']]
    # for all columns has "Giá" in the name, convert to value then multiply by 1000, set as integer
    for col in df.columns:
        if 'Giá' in col:
            try:
                df[col] = df[col].astype(float)*1000
                df[col] = df[col].astype(int)
            except:
                pass
    return df

def price_board (symbol_ls):
    """
    This function returns the trading price board of a target stocks list.
    Args:
        symbol_ls (:obj:`str`, required): STRING list of symbols separated by "," without any space. Ex: "TCB,SSI,BID"
    """ 
    data = requests.get('https://apipubaws.tcbs.com.vn/stock-insight/v1/stock/second-tc-price?tickers={}'.format(symbol_ls)).json()
    df = json_normalize(data['data'])
    # drop columns named seq
    df.drop(columns=['seq'], inplace=True)
    df = df[['t', 'cp', 'fv', 'mav', 'nstv', 'nstp', 'rsi', 'macdv', 'macdsignal',
       'tsignal', 'avgsignal', 'ma20', 'ma50', 'ma100', 'session', 'mw3d',
       'mw1m', 'mw3m', 'mw1y', 'rs3d', 'rs1m', 'rs3m', 'rs1y', 'rsavg', 'hp1m',
       'hp3m', 'hp1y', 'lp1m', 'lp3m', 'lp1y', 'hp1yp', 'lp1yp', 'pe', 'pb',
       'roe', 'oscore', 'av', 'bv', 'ev', 'hmp', 'mscore', 'delta1m',
       'delta1y', 'vnipe', 'vnipb', 'vnid3d', 'vnid1m', 'vnid3m', 'vnid1y']]
    df = df.rename(columns={'t' : 'Mã CP', 'cp' : 'Giá', 'fv' : 'KLBD/TB5D', 'mav' : 'T.độ GD', 'nstv' : 'KLGD ròng(CM)', 'nstp' : '%KLGD ròng (CM)', 'rsi' : 'RSI', 'macdv' : 'MACD Hist', 'macdsignal' : 'MACD Signal', 'tsignal' : 'Tín hiệu KT', 'avgsignal' : 'Tín hiệu TB động', 'ma20' : 'MA20', 'ma50' : 'MA50', 'ma100' : 'MA100', 'session' : 'Phiên +/- ', 'mscore' : 'Đ.góp VNINDEX', 'pe' : 'P/E', 'pb' : 'P/B', 'roe' : 'ROE', 'oscore' : 'TCRating', 'ev' : 'TCBS định giá', 'mw3d' : '% thay đổi giá 3D', 'mw1m' : '% thay đổi giá 1M', 'mw3m' : '% thay đổi giá 3M', 'mw1y' : '% thay đổi giá 1Y', 'rs3d' : 'RS 3D', 'rs1m' : 'RS 1M', 'rs3m' : 'RS 3M', 'rs1y' : 'RS 1Y', 'rsavg' : 'RS TB', 'hp1m' : 'Đỉnh 1M', 'hp3m' : 'Đỉnh 3M', 'hp1y' : 'Đỉnh 1Y', 'lp1m' : 'Đáy 1M', 'lp3m' : 'Đáy 3M', 'lp1y' : 'Đáy 1Y', 'hp1yp' : '%Đỉnh 1Y', 'lp1yp' : '%Đáy 1Y', 'delta1m' : '%Giá - %VNI (1M)', 'delta1y' : '%Giá - %VNI (1Y)', 'bv' : 'Khối lượng Dư mua', 'av' : 'Khối lượng Dư bán', 'hmp' : 'Khớp nhiều nhất', 'vnipe':'VNINDEX P/E', 'vnipb':'VNINDEX P/B'})
    return df


def stock_intraday_data (symbol='ACB', page_size=50, page=0, investor_segment=True, headers=tcbs_headers):
    """
    Get intraday stock insights from TCBS Trade Station
    Parameters:
        symbol (str): ticker of the stock
        page_size (int): number of data points per page. Default is 50. You can increase this parameter multiply by 100, for instance, increase to about 1000 to get all data in one trading day.
        page (int): page number. Default is 0. You can ignore this parameter.
        investor_segment (bool): True to get data by investor segment, False to get data by order type. Default is True.
        headers (dict): headers of the request. You can ignore this parameter.
    """
    # if the page_size is greater than 100, loop through the pages to get all data
    if page_size > 100:
        df = pd.DataFrame()
        for i in range(0, page_size//100):
            # create url
            if investor_segment == True:
                url = f"https://apipubaws.tcbs.com.vn/stock-insight/v1/intraday/{symbol}/investor/his/paging?page={i}&size=100&headIndex=-1"
            elif investor_segment == False:
                url = f'https://apipubaws.tcbs.com.vn/stock-insight/v1/intraday/{symbol}/his/paging?page={i}&size=100&headIndex=-1'
            # send request to get response
            response = requests.request("GET", url, headers=headers)
            # if response status is 200, then get data from response
            if response.status_code == 200:
                response = response.json()
                df_temp = pd.DataFrame(response['data'])
                df_temp['ticker'] = response['ticker']
                df = pd.concat([df, df_temp])
            # if response status is not 200, then stop the loop
            else:
                break
    else:
        # create url
        if investor_segment == True:
            url = f"https://apipubaws.tcbs.com.vn/stock-insight/v1/intraday/{symbol}/investor/his/paging?page={page}&size={page_size}&headIndex=-1"
        elif investor_segment == False:
            url = f'https://apipubaws.tcbs.com.vn/stock-insight/v1/intraday/{symbol}/his/paging?page={page}&size={page_size}&headIndex=-1'
        # send request to get response
        response = requests.request("GET", url, headers=headers)
        # if response status is 200, then get data from response
        if response.status_code == 200:
            response = response.json()
            df = pd.DataFrame(response['data'])
            df['ticker'] = response['ticker']
        # if response status is not 200, then return None and print the error message
        else:
            print(response['message'])
            return None
    df.drop(columns=['cp', 'rcp'], inplace=True)
    df.rename(columns={'ap': 'averagePrice', 'p':'price', 'v': 'volume', 'a': 'orderType', 't': 'time', 'n': 'orderCount', 'type': 'investorType', 'pcp': 'prevPriceChange'}, inplace=True)
    if investor_segment == True:
        df = df[['ticker', 'time', 'orderType', 'investorType', 'volume', 'averagePrice', 'orderCount', 'prevPriceChange']]
        # rename values of orderType, SD to Sell Down, BU to Buy Up
        df['orderType'] = df['orderType'].replace({'SD': 'Sell Down', 'BU': 'Buy Up'})
    elif investor_segment == False:
        df = df[['ticker', 'time', 'orderType', 'volume', 'price', 'prevPriceChange']]
        df['orderType'] = df['orderType'].replace({'SD': 'Sell Down', 'BU': 'Buy Up'})
    df.reset_index(drop=True, inplace=True)
    return df


