from .config import *

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
    response = requests.request("GET", url, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        df = pd.DataFrame(response_data)
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
    else:
        print(f"Error in API response", "\n")
        
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
