from .config import *

## STOCK TRADING HISTORICAL DATA
def stock_historical_data (symbol='TCB', start_date='2023-06-01', end_date='2023-06-17', resolution='1D', type='stock', beautify=True, decor=False, source='DNSE'): # DNSE source (will be published on vnstock)
    """
    Get historical price data from entrade.com.vn. The unit price is VND.
    Parameters:
        symbol (str): ticker of a stock or index. Available indices are: VNINDEX, VN30, HNX, HNX30, UPCOM, VNXALLSHARE, VN30F1M, VN30F2M, VN30F1Q, VN30F2Q
        from_date (str): start date of the historical price data
        to_date (str): end date of the historical price data
        resolution (str): resolution of the historical price data. Default is '1D' (daily), other options are '1' (1 minute), 15 (15 minutes), 30 (30 minutes), '1H' (hourly). For stock, the limit of 90 days is applied to resolution 1, 15, 30, 1H.
        type (str): stock, index, or derivative. Default is 'stock'
        beautify (bool): if True, convert open, high, low, close to VND for stock symbols. Default is True which means the unit price is thousands VND
        decor (bool): if True, rename columns to Title Case (Open, High, Low, Close instead of open, high, low, close) and set Time column as index. Default is False. This option help to integrate vnstock with other libraries such as TA-Lib out of the box.
        source (str): data source. Default is 'DNSE' EntradeX, other options are 'TCBS' (Only applicable for the `Day` resolution, longterm data)
        headers (dict): headers of the request
    Returns:
        :obj:`pandas.DataFrame`:
        | time | open | high | low | close | volume |
        | ----------- | ---- | ---- | --- | ----- | ------ |
        | YYYY-mm-dd  | xxxx | xxxx | xxx | xxxxx | xxxxxx |
    """
    if source.upper() == 'DNSE':
        df = ohlc_data(symbol, start_date, end_date, resolution, type, headers=entrade_headers)
    elif source.upper() == 'TCBS':
        if resolution == '1D':
            resolution = 'D'
            df = longterm_ohlc_data(symbol, start_date, end_date, resolution, type, headers=tcbs_headers)
        else:
            print('TCBS only support longterm daily data. Please set resolution to 1D')
            return None
    df = df[['time', 'open', 'high', 'low', 'close', 'volume', 'ticker']]
    if beautify:
        if type == 'stock':
            df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']] * 1000
            # convert open, high, low, close to int
            df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(int)
    if decor == True:
        # Rename columns to Titlecase
        df.columns = df.columns.str.title()
        # set time as index
        df = df.set_index('Time')
    return df

def longterm_ohlc_data (symbol='REE', start_date='2022-01-01', end_date='2023-10-31', resolution='D', type='stock', headers=tcbs_headers):
    """
    Get longterm OHLC data from TCBS
    Parameters:
    """
    # convert date difference to number of days
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    delta = (end_date - start_date).days
    # convert end_date to timestamp
    end_date_stp = int(end_date.timestamp())
    print(f'Time range is {delta} days. Looping through {delta // 365 + 1} requests')
    # if delta is greater than 365 days loop through multiple requests to get full data
    if delta > 365:
        df = pd.DataFrame()
        while delta > 365:
            if type in ['stock', 'index']:
                url = f"https://apipubaws.tcbs.com.vn/stock-insight/v2/stock/bars-long-term?ticker={symbol}&type={type}&resolution={resolution}&to={end_date_stp}&countBack=365"
            elif type == 'derivative':
                url = f'https://apipubaws.tcbs.com.vn/futures-insight/v2/stock/bars-long-term?ticker={symbol}&type=derivative&resolution={resolution}&to={end_date_stp}&countBack=365'
            response = requests.request("GET", url, headers=headers)
            status_code = response.status_code
            if status_code == 200:
                data = response.json()
                df_temp = pd.DataFrame(data['data'])
                # convert tradingDate to time column
                df_temp['time'] = pd.to_datetime(df_temp['tradingDate']).dt.strftime('%Y-%m-%d')
                # drop tradingDate column
                df_temp.drop('tradingDate', axis=1, inplace=True)
                # append df_temp to df
                df = pd.concat([df_temp, df], ignore_index=True)
                # update end_date_stp in miliseconds and delta
                end_date_stp = int(datetime.strptime(df['time'].min(), '%Y-%m-%d').timestamp())
                delta = delta - 365
            else:
                print(f'Error {status_code}. {response.text}')
        # get the remaining data
        if type in ['stock', 'index']:
            url = f"https://apipubaws.tcbs.com.vn/stock-insight/v2/stock/bars-long-term?ticker={symbol}&type={type}&resolution={resolution}&to={end_date_stp}&countBack={delta}"
        elif type == 'derivative':
            url = f'https://apipubaws.tcbs.com.vn/futures-insight/v2/stock/bars-long-term?ticker={symbol}&type=derivative&resolution={resolution}&to={end_date_stp}&countBack={delta}'
        response = requests.request("GET", url, headers=headers)
        status_code = response.status_code
        if status_code == 200:
            data = response.json()
            df_temp = pd.DataFrame(data['data'])
            # convert tradingDate to time column
            df_temp['time'] = pd.to_datetime(df_temp['tradingDate']).dt.strftime('%Y-%m-%d')
            # drop tradingDate column
            df_temp.drop('tradingDate', axis=1, inplace=True)
            # append df_temp to df
            df = pd.concat([df_temp, df], ignore_index=True)
        else:
            print(f'Error {status_code}. {response.text}')
            # select data from start_date to end_date
        df = df[(df['time'] >= start_date.strftime('%Y-%m-%d')) & (df['time'] <= end_date.strftime('%Y-%m-%d'))]
        # devide price by 1000
        df['ticker'] = symbol
        # filter data from df to get data from start_date to end_date
        df = df[(df['time'] >= start_date.strftime('%Y-%m-%d')) & (df['time'] <= end_date.strftime('%Y-%m-%d'))]
        if type == 'stock':
            df[['open', 'high', 'low', 'close']] = round(df[['open', 'high', 'low', 'close']] / 1000, 2)
        # convert df columns open, high, low, close, volume to float, volume to int
        df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
        df['volume'] = df['volume'].astype(int)
        return df
    else:
        if type in ['stock', 'index']:
            url = f"https://apipubaws.tcbs.com.vn/stock-insight/v2/stock/bars-long-term?ticker={symbol}&type={type}&resolution={resolution}&to={end_date_stp}&countBack={delta}"
        elif type == 'derivative':
            url = f'https://apipubaws.tcbs.com.vn/futures-insight/v2/stock/bars-long-term?ticker={symbol}&type=derivative&resolution={resolution}&to={end_date_stp}&countBack={delta}'
        response = requests.request("GET", url, headers=headers)
        status_code = response.status_code
        if status_code == 200:
            data = response.json()
            df = pd.DataFrame(data['data'])
            # convert tradingDate to time column
            df['time'] = pd.to_datetime(df['tradingDate']).dt.strftime('%Y-%m-%d')
            # drop tradingDate column
            df.drop('tradingDate', axis=1, inplace=True)
            df['ticker'] = symbol
            df = df[(df['time'] >= start_date.strftime('%Y-%m-%d')) & (df['time'] <= end_date.strftime('%Y-%m-%d'))]
            if type == 'stock':
                df[['open', 'high', 'low', 'close']] = round(df[['open', 'high', 'low', 'close']] / 1000, 2)
            # convert df columns open, high, low, close, volume to float, volume to int
            df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
            df['volume'] = df['volume'].astype(int)
            return df
        else:
            print(f'Error {status_code}. {response.text}')
            return None
        
def ohlc_data (symbol, start_date='2023-06-01', end_date='2023-06-17', resolution='1D', type='stock', headers=entrade_headers): # DNSE source (will be published on vnstock)
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
    start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
    # if resolution is not 1D, then calculate the start date is last 90 days from end_date
    if resolution != '1D':
        new_start_timestamp = int(datetime.now().timestamp()) - 90 * 24 * 60 * 60
        new_end_timestamp = int(datetime.now().timestamp()) - 90 * 24 * 60 * 60
        # if new_from_timestamp > from_timestamp, then print a notice to user that data is limit to 90 days
        if end_timestamp < new_end_timestamp:
            print("The 'end_date' value in the report should be no more than 90 days from today for all resolutions shorter than 1 day.", "\n")
        elif new_start_timestamp > start_timestamp:
            start_timestamp = new_start_timestamp
            print("The retrieval of stock data is restricted to the most recent 90 days from today for all resolutions shorter than 1 day.", "\n")
    url = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/{type}?from={start_timestamp}&to={end_timestamp}&symbol={symbol}&resolution={resolution}"
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
            # format df['time'] to datetime string with format %Y-%m-%d %H:%M:%S
            df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        # convert df columns open, high, low, close, volume to float, volume to int
        df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
        df['volume'] = df['volume'].astype(int)
    else:
        print(f"Error in API response {response.text}", "\n")
    return df