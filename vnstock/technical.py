from .config import *

## STOCK TRADING HISTORICAL DATA
def stock_historical_data (symbol='TCB', start_date='2023-06-01', end_date='2023-06-17', resolution='1D', type='stock', beautify=True, headers=entrade_headers): # DNSE source (will be published on vnstock)
    """
    Get historical price data from entrade.com.vn. The unit price is VND.
    Parameters:
        symbol (str): ticker of a stock or index. Available indices are: VNINDEX, VN30, HNX, HNX30, UPCOM, VNXALLSHARE, VN30F1M, VN30F2M, VN30F1Q, VN30F2Q
        from_date (str): start date of the historical price data
        to_date (str): end date of the historical price data
        resolution (str): resolution of the historical price data. Default is '1D' (daily), other options are '1' (1 minute), 15 (15 minutes), 30 (30 minutes), '1H' (hourly)
        type (str): stock, index, or derivative. Default is 'stock'
        beautify (bool): if True, convert open, high, low, close to VND for stock symbols. Default is True
        headers (dict): headers of the request
    Returns:
        :obj:`pandas.DataFrame`:
        | time | open | high | low | close | volume |
        | ----------- | ---- | ---- | --- | ----- | ------ |
        | YYYY-mm-dd  | xxxx | xxxx | xxx | xxxxx | xxxxxx |
    """
    df = ohlc_data(symbol, start_date, end_date, resolution, type, beautify, headers)
    return df

def ohlc_data (symbol, start_date='2023-06-01', end_date='2023-06-17', resolution='1D', type='stock', beautify=True, headers=entrade_headers): # DNSE source (will be published on vnstock)
    """
    Get historical price data from entrade.com.vn. The unit price is VND.
    Parameters:
        symbol (str): ticker of a stock or index. Available indices are: VNINDEX, VN30, HNX, HNX30, UPCOM, VNXALLSHARE, VN30F1M, VN30F2M, VN30F1Q, VN30F2Q
        from_date (str): start date of the historical price data
        to_date (str): end date of the historical price data
        resolution (str): resolution of the historical price data. Default is '1D' (daily), other options are '1' (1 minute), 15 (15 minutes), 30 (30 minutes), '1H' (hourly)
        type (str): stock or index. Default is 'stock'
        beautify (bool): if True, convert open, high, low, close to VND for stock symbols. Default is True
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
    # if resolution is not 1D, then calculate the start date is last 90 days from end_date
    if resolution != '1D':
        new_from_timestamp = to_timestamp - 90 * 24 * 60 * 60
        # if new_from_timestamp > from_timestamp, then print a notice to user that data is limit to 90 days
        if new_from_timestamp > from_timestamp:
            from_timestamp = new_from_timestamp
            print("Data is limited to the last 90 days for all resolution in minutes", "\n")
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
        # if type=stock and beautify=True, then convert open, high, low, close to VND, elif type=index keep as is
        if type == 'stock' and beautify == True:
            df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']] * 1000
            # convert open, high, low, close to int
            df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(int)
        else:
            pass
    else:
        print(f"Error in API response {response.text}", "\n")
    return df
