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
  'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
  'DNT': '1',
  'Accept-language': 'vi',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
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

fmarket_headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "vi",
    "content-type": "application/json",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "referrer": "https://fmarket.vn/"
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

fmarket_headers = {
  'authority': 'api.fmarket.vn',
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'vi',
  'content-type': 'application/json',
  'dnt': '1',
  'origin': 'https://fmarket.vn',
  'referer': 'https://fmarket.vn/',
  'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
}

def api_request(url, headers=ssi_headers):
    r = requests.get(url, headers).json()
    return r


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


# ## MARKET WATCH

# def market_top_mover (report_name): #Value, Losers, Gainers, Volume, ForeignTrading, NewLow, Breakout, NewHigh
#     """
#     This function returns the list of Top Stocks by one of criteria: 'Value', 'Losers', 'Gainers', 'Volume', 'ForeignTrading', 'NewLow', 'Breakout', 'NewHigh'.
#     Args:
#         report_name(:obj:`str`, required): name of the report
#     """
#     ls1 = ['Gainers', 'Losers', 'Value', 'Volume']
#     # ls2 = ['ForeignTrading', 'NewLow', 'Breakout', 'NewHigh']
#     if report_name in ls1:
#         url = 'https://fiin-market.ssi.com.vn/TopMover/GetTop{}?language=vi&ComGroupCode=All'.format(report_name)
#     elif report_name == 'ForeignTrading':
#         url = 'https://fiin-market.ssi.com.vn/TopMover/GetTopForeignTrading?language=vi&ComGroupCode=All&Option=NetBuyVol'
#     elif report_name == 'NewLow':
#         url = 'https://fiin-market.ssi.com.vn/TopMover/GetTopNewLow?language=vi&ComGroupCode=All&TimeRange=ThreeMonths'
#     elif report_name == 'Breakout':
#         url = 'https://fiin-market.ssi.com.vn/TopMover/GetTopBreakout?language=vi&ComGroupCode=All&TimeRange=OneWeek&Rate=OnePointFive'
#     elif report_name == 'NewHigh':
#         url = 'https://fiin-market.ssi.com.vn/TopMover/GetTopNewHigh?language=vi&ComGroupCode=All&TimeRange=ThreeMonths'
#     r = api_request(url)
#     df = pd.DataFrame(r['items'])
#     return df


# def fr_trade_heatmap (exchange, report_type): 
#     """
#     This function returns the foreign investors trading insights which is being rendered as the heatmap on SSI iBoard
#     Args:
#         exchange (:obj:`str`, required): Choose All, HOSE, HNX, or UPCOM.
#         report_type (:obj:`str`, required): choose one of these report types: FrBuyVal, FrSellVal, FrBuyVol, FrSellVol, Volume, Value, MarketCap
#     """
#     url = 'https://fiin-market.ssi.com.vn/HeatMap/GetHeatMap?language=vi&Exchange={}&Criteria={}'.format(exchange, report_type)
#     r = api_request(url)
#     concat_ls = []
#     for i in range(len(r['items'])):
#         for j in range(len(r['items'][i]['sectors'])):
#             name = r['items'][i]['sectors'][j]['name']
#             rate = r['items'][i]['sectors'][j]['rate']
#             df = json_normalize(r['items'][i]['sectors'][j]['tickers'])
#             df['industry_name'] = name
#             df['rate'] = rate
#             concat_ls.append(df)
#     combine_df = pd.concat(concat_ls)
#     return combine_df

# # GET MARKET IN DEPT DATA - INDEX SERIES

# def get_index_series(index_code='VNINDEX', time_range='OneYear', headers=ssi_headers):
#     """
#     Retrieve the Stock market index series, maximum in 5 years
#     Args:
#         index_code (:obj:`str`, required): Use one of the following code'VNINDEX', 'VN30', 'HNXIndex', 'HNX30', 'UpcomIndex', 'VNXALL',
#                                         'VN100','VNALL', 'VNCOND', 'VNCONS','VNDIAMOND', 'VNENE', 'VNFIN',
#                                         'VNFINLEAD', 'VNFINSELECT', 'VNHEAL', 'VNIND', 'VNIT', 'VNMAT', 'VNMID',
#                                         'VNREAL', 'VNSI', 'VNSML', 'VNUTI', 'VNX50'. You can get the complete list of the latest indices from `get_latest_indices()` function
#         time_range (:obj: `str`, required): Use one of the following values 'OneDay', 'OneWeek', 'OneMonth', 'ThreeMonth', 'SixMonths', 'YearToDate', 'OneYear', 'ThreeYears', 'FiveYears'
#     """
#     url = f"https://fiin-market.ssi.com.vn/MarketInDepth/GetIndexSeries?language=vi&ComGroupCode={index_code}&TimeRange={time_range}&id=1"
#     payload={}
#     response = requests.request("GET", url, headers=headers, data=payload)
#     result = json_normalize(response.json()['items'])
#     return result

# def get_latest_indices(headers=ssi_headers):
#     """
#     Retrieve the latest indices values
#     """
#     url = "https://fiin-market.ssi.com.vn/MarketInDepth/GetLatestIndices?language=vi&pageSize=999999&status=1"
#     payload={}
#     response = requests.request("GET", url, headers=headers, data=payload)
#     result = json_normalize(response.json()['items'])
#     return result



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
