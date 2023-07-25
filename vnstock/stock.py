# Copyright 2022 Thinh Vu @ GitHub
# See LICENSE for details.

# from .utils import *
import pandas as pd
import requests
from pandas import json_normalize
from io import BytesIO
import time
from datetime import datetime, timedelta
import json

# API request config for SSI API endpoints
ssi_headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
        'DNT': '1',
        'sec-ch-ua-mobile': '?0',
        'X-Fiin-Key': 'KEY',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Fiin-User-ID': 'ID',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        'X-Fiin-Seed': 'SEED',
        'sec-ch-ua-platform': 'Windows',
        'Origin': 'https://iboard.ssi.com.vn',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://iboard.ssi.com.vn/',
        'Accept-Language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7'
        }

entrade_headers = {
  'authority': 'services.entrade.com.vn',
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'en-US,en;q=0.9',
  'dnt': '1',
  'origin': 'https://banggia.dnse.com.vn',
  'referer': 'https://banggia.dnse.com.vn/',
  'sec-ch-ua': '"Edge";v="114", "Chromium";v="114", "Not=A?Brand";v="24"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'cross-site',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0'
}

tcbs_headers = {
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
  'DNT': '1',
  'Accept-language': 'vi',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Referer': 'https://tcinvest.tcbs.com.vn/',
  'sec-ch-ua-platform': '"Windows"'
}

vps_headers = {
  'Accept': 'application/json, text/plain, */*',
  'Accept-Language': 'en-US,en;q=0.9',
  'Connection': 'keep-alive',
  'DNT': '1',
  'Origin': 'https://banggia.vps.com.vn',
  'Referer': 'https://banggia.vps.com.vn/',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-site',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"'
}

# Rong Viet - Live Dragon
rv_cookie = 'RV08835624=080035c91e77d96a1dcd7d9668d15032dca1c5c44e92ef5bbacedcc05701ff85c9486d38fb81e83857d5672616b9e3546504ee4846; _ga_KN4YPTLVCF=GS1.1.1690211515.1.0.1690211515.0.0.0; _gid=GA1.3.1634163694.1690211515; _gat_gtag_UA_120090926_1=1; _fbp=fb.2.1690211516077.1111198076; JSESSIONID=BFEB38A8B8419EEEC39DF45490E1B22D; vdsc-liv=\u00210CIhC2srW+VXY3rGJTT3LEhTmJvzwWLF5bKAMvgEjULUV+lBtkyTYFCLv7njgHRB4TgCdXik8NDWPQ==; hideMarketChartCKName=0; allCustomGroupsCkName=ALL_DEFAULT_GROUP_ID%23%23%23%23%23%23%23%23CTD%3BDHG%3BDRC%3BFPT%3BHPG%3BHSG%3BKDC%3BMWG%3BNT2%3BPAC%3BPC1%3BPNJ%3BTAC%3BVCB%3BVDS%3BVGC%3BVJC%3BVNM%3B%23%23%23%23%23%23%23%23T%C3%B9y%20ch%E1%BB%8Dn; rv_avraaaaaaaaaaaaaaaa_session_=DPHJFAEBJMBKENBPDOLDBOKIJCPLBLGFPHHGOCJEHFLMNGOGJINNIAOOIOPCNEILMDODFNCOCEGJIMDEHDNABIPKIJNKFFJCBEHPHADOFOLCEJEFFABNAAMIOLLMAEFI; _ga=GA1.1.1224611093.1690211515; _ga_D36ML1235R=GS1.1.1690211525.1.1.1690211543.0.0.0; RV9cd20160034=08557ab163ab2000054ec4478471ef19572f6aa45f46e6023a0505610ff398cf65052602d337f301084048ab69113000c7d3b36391060024abdc7de0506ec20cf57eadcbff388725325c25c6632a4cbda9a1e282112bd2a9d7d1e1c4471b850a'

rv_headers = {
  'Accept': 'application/json, text/javascript, */*; q=0.01',
  'Accept-Language': 'en-US,en;q=0.9',
  'Connection': 'keep-alive',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'DNT': '1',
  'Origin': 'https://livedragon.vdsc.com.vn',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua': '"Edge";v="114", "Chromium";v="114", "Not=A?Brand";v="24"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"'
}

def api_request(url, headers=ssi_headers):
    r = requests.get(url, headers).json()
    return r

## STOCK LISTING
def listing_companies (path='https://raw.githubusercontent.com/thinh-vu/vnstock/beta/data/listing_companies_enhanced-2023.csv'):
    """
    This function returns the list of all available stock symbols from a csv file or a live api request.
    Parameters: 
        path (str): The path of the csv file to read from. Default is the path of the file 'listing_companies_enhanced-2023.csv'. You can find the latest updated file at `https://github.com/thinh-vu/vnstock/tree/main/src`
    Returns: df (DataFrame): A pandas dataframe containing the stock symbols and other information. 
    """
    df = pd.read_csv(path)
    return df

def company_overview (symbol):
    """
    This function returns the company overview of a target stock symbol
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
    """
    data = requests.get(f'https://apipubaws.tcbs.com.vn/tcanalysis/v1/ticker/{symbol}/overview').json()
    df = json_normalize(data)
    # Rearrange columns
    df = df[['ticker', 'exchange', 'industry', 'companyType',
            'noShareholders', 'foreignPercent', 'outstandingShare', 'issueShare',
            'establishedYear', 'noEmployees',  
            'stockRating', 'deltaInWeek', 'deltaInMonth', 'deltaInYear', 
            'shortName', 'industryEn', 'industryID', 'industryIDv2', 'website']]
    return df

## STOCK TRADING HISTORICAL DATA
def stock_historical_data (symbol, start_date='2023-06-01', end_date='2023-06-17', resolution='1D', type='stock', headers=entrade_headers): # DNSE source (will be published on vnstock)
    """
    Get historical price data from entrade.com.vn. The unit price is VND.
    Parameters:
        symbol (str): ticker of a stock or index. Available indices are: VNINDEX, VN30, HNX, HNX30, UPCOM, VNXALLSHARE, VN30F1M, VN30F2M, VN30F1Q, VN30F2Q
        from_date (str): start date of the historical price data
        to_date (str): end date of the historical price data
        resolution (str): resolution of the historical price data. Default is '1D' (daily), other options are '1' (1 minute), 15 (15 minutes), 30 (30 minutes), '1H' (hourly)
        type (str): stock, index, or derivative. Default is 'stock'
        headers (dict): headers of the request
    Returns:
        :obj:`pandas.DataFrame`:
        | time | open | high | low | close | volume |
        | ----------- | ---- | ---- | --- | ----- | ------ |
        | YYYY-mm-dd  | xxxx | xxxx | xxx | xxxxx | xxxxxx |
    """
    # if type is stock or index, call the function stock_ohlc
    if type == 'stock' or type == 'index':
        df = stock_ohlc(symbol, start_date, end_date, resolution, type, headers)
    # if type is derivative, call the function derivatives_ohlc
    elif type == 'derivative':
        df = derivatives_ohlc(symbol, start_date, end_date, resolution, headers)
    else:
        raise ValueError('type must be stock, index or derivative')
    return df

def stock_ohlc (symbol, start_date='2023-06-01', end_date='2023-06-17', resolution='1D', type='stock', headers=entrade_headers): # DNSE source (will be published on vnstock)
    """
    Get historical price data from entrade.com.vn. The unit price is VND.
    Parameters:
        symbol (str): ticker of a stock or index. Available indices are: VNINDEX, VN30, HNX, HNX30, UPCOM, VNXALLSHARE, VN30F1M, VN30F2M, VN30F1Q, VN30F2Q
        from_date (str): start date of the historical price data
        to_date (str): end date of the historical price data
        resolution (str): resolution of the historical price data. Default is '1D' (daily), other options are '1' (1 minute), 15 (15 minutes), 30 (30 minutes), '1H' (hourly)
        type (str): stock or index. Default is 'stock'
        headers (dict): headers of the request
    Returns:
        :obj:`pandas.DataFrame`:
        | time | open | high | low | close | volume |
        | ----------- | ---- | ---- | --- | ----- | ------ |
        | YYYY-mm-dd  | xxxx | xxxx | xxx | xxxxx | xxxxxx |
    """
    # add one more day to end_date
    end_date = (datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    # convert from_date, to_date to timestamp
    from_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    to_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
    url = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/{type}?from={from_timestamp}&to={to_timestamp}&symbol={symbol}&resolution={resolution}"
    response = requests.request("GET", url, headers=headers).json()
    df = pd.DataFrame(response)
    df['t'] = pd.to_datetime(df['t'], unit='s') # convert timestamp to datetime
    df = df.rename(columns={'t': 'time', 'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'}).drop(columns=['nextTime'])
    # add symbol column
    df['ticker'] = symbol
    df['time'] = df['time'].dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
    # if resolution is 1D, then convert time to date
    if resolution == '1D':
        df['time'] = df['time'].dt.date
    else:
        pass
    # convert open, high, low, close to VND
    df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']] * 1000
    # convert open, high, low, close to int
    df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(int)
    # if resolution is 1D, then convert time to date
    return df

def derivatives_ohlc (symbol='VN30F1M', from_date='2023-04-01', to_date='2023-07-12', resolution='1D', headers=entrade_headers):
    """
    Get derivatives historical price from DNSE
    Parameters:
        symbol (str): derivative symbol
        from_date (str): start date of the historical price data, format is 'YYYY-MM-DD'
        to_date (str): end date of the historical price data, format is 'YYYY-MM-DD'
        resolution (str): resolution of the historical price data. Default is '1D' (daily), other options are '1' (1 minute), 3 (3 minutes), 5 (5 minutes), 15 (15 minutes), 30 (30 minutes), 45 (45 minutes), '1H' (hourly), '2H' (2 hours), '4H' (4 hours), '1W' (weekly), '1M' (monthly)
        headers (dict): headers of the request
    """
    # convert from_date, to_date to timestamp
    from_timestamp = int(datetime.strptime(from_date, '%Y-%m-%d').timestamp())
    to_timestamp = int(datetime.strptime(to_date, '%Y-%m-%d').timestamp())
    # create url
    url = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/derivative?from={from_timestamp}&to={to_timestamp}&symbol={symbol}&resolution={resolution}"
    # send request to get response
    response = requests.request("GET", url, headers=headers).json()
    df = pd.DataFrame(response)
    # convert timestamp to datetime
    df['t'] = pd.to_datetime(df['t'], unit='s')
    # convert o, h, l, c to int
    df[['o', 'h', 'l', 'c']] = df[['o', 'h', 'l', 'c']].astype(int)
    # rename columns, t for time, o for open, h for high, l for low, c for close, v for volume and drop the nextTime column
    df = df.rename(columns={'t': 'time', 'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'}).drop(columns=['nextTime'])
    # add symbol column
    df['ticker'] = symbol
    # convert time from utc to Asia/Ho_Chi_Minh timezone
    df['time'] = df['time'].dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
    # if resolution is 1D, convert time to date
    if resolution == '1D':
        df['time'] = df['time'].dt.date
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

# TRADING INTELLIGENT
today_val = datetime.now()

def today():
    today = today_val.strftime('%Y-%m-%d')
    return today

def last_xd (day_num): # return the date of last x days
    """
    This function returns the date that X days ago from today in the format of YYYY-MM-DD.
    Args:
        day_num (:obj:`int`, required): numer of days.
    Returns:
        :obj:`str`:
            2022-02-22
    Raises:
        ValueError: raised whenever any of the introduced arguments is not valid.
    """  
    last_xd = (today_val - timedelta(day_num)).strftime('%Y-%m-%d')
    return last_xd

def start_xm (period): # return the start date of x months
    """
    This function returns the start date of X months ago from today in the format of YYYY-MM-DD.
    Args:
        period (:obj:`int`, required): numer of months (period).
    Returns:
        :obj:`str`:
            2022-01-01
    Raises:
        ValueError: raised whenever any of the introduced arguments is not valid.
    """ 
    date = pd.date_range(end=today, periods=period+1, freq='MS')[0].strftime('%Y-%m-%d')
    return date

def stock_intraday_data (symbol='ACB', page_size=50, page=0, headers=tcbs_headers):
    """
    Get intraday stock insights from TCBS Trade Station
    Parameters:
        symbol (str): ticker of the stock
        page_size (int): number of data points per page. Default is 50. You can increase this parameter to about 1000 to get all data in one trading day.
        page (int): page number. Default is 0. You can ignore this parameter.
        headers (dict): headers of the request. You can ignore this parameter.
    """
    # if the page_size is greater than 100, loop through the pages to get all data
    if page_size > 100:
        df = pd.DataFrame()
        for i in range(0, page_size//100):
            # create url
            url = f"https://apipubaws.tcbs.com.vn/stock-insight/v1/intraday/{symbol}/investor/his/paging?page={i}&size=100&headIndex=-1"
            # send request to get response
            response = requests.request("GET", url, headers=headers).json()
            df_temp = pd.DataFrame(response['data'])
            df_temp['ticker'] = response['ticker']
            df = pd.concat([df, df_temp])
    else:
        # create url
        url = f"https://apipubaws.tcbs.com.vn/stock-insight/v1/intraday/{symbol}/investor/his/paging?page={page}&size={page_size}&headIndex=-1"
        # send request to get response
        response = requests.request("GET", url, headers=headers).json()
        df = pd.DataFrame(response['data'])
        df['ticker'] = response['ticker']
    # move ticker column to the first column
    cols = df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df = df[cols]
    # drop columns cp, rcp, pcp
    df.drop(columns=['cp', 'rcp', 'pcp'], inplace=True)
    # rename columns ap to averagePrice, v to volume, a to orderType, t to time, n to orderCount, type to investorType
    df.rename(columns={'ap': 'averagePrice', 'v': 'volume', 'a': 'orderType', 't': 'time', 'n': 'orderCount', 'type': 'investorType'}, inplace=True)
    # arrange columns by ticker, time, orderType, investorType, volume, averagePrice, orderCount
    df = df[['ticker', 'time', 'orderType', 'investorType', 'volume', 'averagePrice', 'orderCount']]
    # rename values of orderType, SD to Sell Down, BU to Buy Up
    df['orderType'] = df['orderType'].replace({'SD': 'Sell Down', 'BU': 'Buy Up'})
    # reset index
    df.reset_index(drop=True, inplace=True)
    return df

# COMPANY OVERVIEW
def company_overview (symbol):
    """
    This function returns the company overview of a target stock symbol
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
    """
    data = requests.get(f'https://apipubaws.tcbs.com.vn/tcanalysis/v1/ticker/{symbol}/overview').json()
    df = json_normalize(data)
    return df


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

def financial_flow(symbol='TCB', report_type='incomestatement', report_range='quarterly'): # incomestatement, balancesheet, cashflow | report_range: 0 for quarterly, 1 for yearly
    """
    This function returns the quarterly financial ratios of a stock symbol. Some of expected ratios are: priceToEarning, priceToBook, roe, roa, bookValuePerShare, etc
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
        report_type (:obj:`str`, required): select one of 3 reports: incomestatement, balancesheet, cashflow.
        report_range (:obj:`str`, required): yearly or quarterly.
    """
    if report_range == 'yearly':
        x = 1
    elif report_range == 'quarterly':
        x = 0
    data = requests.get(f'https://apipubaws.tcbs.com.vn/tcanalysis/v1/finance/{symbol}/{report_type}', params={'yearly': x, 'isAll':'true'}).json()
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

## MARKET WATCH

def market_top_mover (report_name): #Value, Losers, Gainers, Volume, ForeignTrading, NewLow, Breakout, NewHigh
    """
    This function returns the list of Top Stocks by one of criteria: 'Value', 'Losers', 'Gainers', 'Volume', 'ForeignTrading', 'NewLow', 'Breakout', 'NewHigh'.
    Args:
        report_name(:obj:`str`, required): name of the report
    """
    ls1 = ['Gainers', 'Losers', 'Value', 'Volume']
    # ls2 = ['ForeignTrading', 'NewLow', 'Breakout', 'NewHigh']
    if report_name in ls1:
        url = 'https://fiin-market.ssi.com.vn/TopMover/GetTop{}?language=vi&ComGroupCode=All'.format(report_name)
    elif report_name == 'ForeignTrading':
        url = 'https://fiin-market.ssi.com.vn/TopMover/GetTopForeignTrading?language=vi&ComGroupCode=All&Option=NetBuyVol'
    elif report_name == 'NewLow':
        url = 'https://fiin-market.ssi.com.vn/TopMover/GetTopNewLow?language=vi&ComGroupCode=All&TimeRange=ThreeMonths'
    elif report_name == 'Breakout':
        url = 'https://fiin-market.ssi.com.vn/TopMover/GetTopBreakout?language=vi&ComGroupCode=All&TimeRange=OneWeek&Rate=OnePointFive'
    elif report_name == 'NewHigh':
        url = 'https://fiin-market.ssi.com.vn/TopMover/GetTopNewHigh?language=vi&ComGroupCode=All&TimeRange=ThreeMonths'
    r = api_request(url)
    df = pd.DataFrame(r['items'])
    return df


def fr_trade_heatmap (exchange, report_type): 
    """
    This function returns the foreign investors trading insights which is being rendered as the heatmap on SSI iBoard
    Args:
        exchange (:obj:`str`, required): Choose All, HOSE, HNX, or UPCOM.
        report_type (:obj:`str`, required): choose one of these report types: FrBuyVal, FrSellVal, FrBuyVol, FrSellVol, Volume, Value, MarketCap
    """
    url = 'https://fiin-market.ssi.com.vn/HeatMap/GetHeatMap?language=vi&Exchange={}&Criteria={}'.format(exchange, report_type)
    r = api_request(url)
    concat_ls = []
    for i in range(len(r['items'])):
        for j in range(len(r['items'][i]['sectors'])):
            name = r['items'][i]['sectors'][j]['name']
            rate = r['items'][i]['sectors'][j]['rate']
            df = json_normalize(r['items'][i]['sectors'][j]['tickers'])
            df['industry_name'] = name
            df['rate'] = rate
            concat_ls.append(df)
    combine_df = pd.concat(concat_ls)
    return combine_df

# GET MARKET IN DEPT DATA - INDEX SERIES

def get_index_series(index_code='VNINDEX', time_range='OneYear', headers=ssi_headers):
    """
    Retrieve the Stock market index series, maximum in 5 years
    Args:
        index_code (:obj:`str`, required): Use one of the following code'VNINDEX', 'VN30', 'HNXIndex', 'HNX30', 'UpcomIndex', 'VNXALL',
                                        'VN100','VNALL', 'VNCOND', 'VNCONS','VNDIAMOND', 'VNENE', 'VNFIN',
                                        'VNFINLEAD', 'VNFINSELECT', 'VNHEAL', 'VNIND', 'VNIT', 'VNMAT', 'VNMID',
                                        'VNREAL', 'VNSI', 'VNSML', 'VNUTI', 'VNX50'. You can get the complete list of the latest indices from `get_latest_indices()` function
        time_range (:obj: `str`, required): Use one of the following values 'OneDay', 'OneWeek', 'OneMonth', 'ThreeMonth', 'SixMonths', 'YearToDate', 'OneYear', 'ThreeYears', 'FiveYears'
    """
    url = f"https://fiin-market.ssi.com.vn/MarketInDepth/GetIndexSeries?language=vi&ComGroupCode={index_code}&TimeRange={time_range}&id=1"
    payload={}
    response = requests.request("GET", url, headers=headers, data=payload)
    result = json_normalize(response.json()['items'])
    return result

def get_latest_indices(headers=ssi_headers):
    """
    Retrieve the latest indices values
    """
    url = "https://fiin-market.ssi.com.vn/MarketInDepth/GetLatestIndices?language=vi&pageSize=999999&status=1"
    payload={}
    response = requests.request("GET", url, headers=headers, data=payload)
    result = json_normalize(response.json()['items'])
    return result

# -----------------------------------------------------------------
# STOCK SCREENER

def stock_screening_insights (params, size=50, id=None, headers=tcbs_headers):
    """
    Get stock screening insights from TCBS Stock Screener
    Parameters:
        params (dict): a dictionary of parameters and their values for the stock screening. The keys should be the names of the filters, and the values should be either a single value or a tuple of two values (min and max) for the filter. For example:
            params = {
                "exchangeName": "HOSE,HNX,UPCOM",
                "epsGrowth1Year": (0, 1000000)
            }
        siz (int): number of data points per page. Default is 50. You can increase this parameter to about 1700 to get all data in one trading day.
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
    df = pd.DataFrame(response['searchData']['pageContent'])
    return df


# -----------------------------------------------------------------
# DERIVATIVES

# A function to get derivatives data from livedragon
def derivatives_historical_match (symbol='VN30F2308', date='2023-07-24', cookie=rv_cookie, headers=rv_headers):
    """
    Get derivatives historical price data from Live Dragon website (CK Rong Viet)
    Parameters:
        symbol (str, required): ticker of the stock
        date (str, required): date of the historical price data
        cookie (str, required): cookie of the request. Visit https://livedragon.vdsc.com.vn/all/all.rv. Open Developer Tools (F12 or Ctrl + Shift + I or Cmd + Option + I on macOS) > Navigate to Network > Choose Fetch/XHR > Select any request > Find Cookie in Header > Copy value.
        headers (dict): headers of the request. You can ignore this parameter.
    """
    # add cookie to headers
    headers['Cookie'] = cookie
    url = "https://livedragon.vdsc.com.vn/general/intradaySearch.rv"
    # convert date to dd/mm/yyyy format
    date = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
    payload = f"stockCode={symbol}&boardDate={date}"
    response = requests.request("POST", url, headers=headers, data=payload).json()
    df = pd.DataFrame(response['list'])
    # move `Code` column to the first column
    df = df[['Code'] + [col for col in df.columns if col != 'Code']]
    return df


# DATA EXPORT

# # Import required modules
# from google.colab import auth
# auth.authenticate_user()
# import gspread
# from google.auth import default
# from gspread_dataframe import set_with_dataframe

# # A function to export data to Google Sheets, support either with a whole sheet or a specific range
# def export_to_sheets (dataframe, sheet_file='vnstock_data_export', sheet_name=None, target_range=None, max_rows=1000, max_cols=30):
#     """
#     Export dataframe to Google Sheets
#     Parameters:
#         dataframe (pandas.DataFrame): Dataframe to export
#         sheet_file (str): Name of the Google Sheets file to export to
#         sheet_name (str): Name of the sheet to export to
#         target_range (str): Range to export to, e.g. 'A1:B2'
#         max_rows (int): Maximum number of rows to create the Google Sheets file.
#         max_cols (int): Maximum number of columns to create the Google Sheets file.
#     """
#     # If sheet_name is not specified, use the default sheet name
#     creds, _ = default()
#     gc = gspread.authorize(creds)
#     sh = gc.create(sheet_file)
#     if sheet_name is None:
#         worksheet = gc.open(sheet_file).sheet1
#     else:
#         worksheet = sh.add_worksheet(title=sheet_name, rows=max_rows, cols=max_cols)
#     # If range is not specified, export the whole dataframe, else export the dataframe to the specified range
#     if range is None:
#         set_with_dataframe(worksheet, dataframe, include_index=False, include_column_header=True, resize=True)
#     else:
#         cell_list = worksheet.range(target_range)
#         for cell, value in zip(cell_list, df.values.flatten()):
#             cell.value = value
#         worksheet.update_cells(cell_list)
#     print('Exported to Google Sheets successfully!')