from .stock import *

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