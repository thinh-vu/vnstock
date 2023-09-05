from .stock import *
from bs4 import BeautifulSoup

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


# COMPANY OVERVIEW
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

# RECENTLY ADDED -------

def company_profile (symbol='TCB', headers=tcbs_headers):
    """
    Return a DataFrame of company overview data.
    Parameters:
    ticker (str): ticker of the company, default is 'TCB', other tickers available can be obtained from the function `listing_companies()`.
    """
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/company/{symbol}/overview"
    response = requests.request("GET", url, headers=headers, data={}).json()
    df = json_normalize(response)
    df['ticker'] = symbol
    # convert text from html to plain text for all columns in the df, add error handling
    for col in df.columns:
        try:
            df[col] = df[col].apply(lambda x: BeautifulSoup(x, 'html.parser').get_text())
            df[col] = df[col].str.replace('\n', ' ')
        except:
            pass
    return df

def company_large_shareholders (symbol='TCB', headers=tcbs_headers):
    """
    Return a DataFrame of company large share holders data.
    Parameters:
    ticker (str): ticker of the company, default is 'TCB', other tickers available can be obtained from the function `listing_companies()`.
    """
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/company/{symbol}/large-share-holders"
    response = requests.request("GET", url, headers=headers, data={}).json()
    df = json_normalize(response['listShareHolder'])
    df['ticker'] = symbol
    # rename columns 'name' to shareHolder, ownPercent to shareOwnPercent
    df.rename(columns={'name': 'shareHolder', 'ownPercent': 'shareOwnPercent'}, inplace=True)
    df.drop(columns=['no'], inplace=True)
    return df

def ticker_fundamental_ratio (symbol='TCB', mode='simplify', missing_pct=0.8, headers=tcbs_headers):
    """
    Return a DataFrame of company tooltip data.
    Parameters:
    ticker (str): ticker of the company, default is 'TCB', other tickers available can be obtained from the function `listing_companies()`.
    mode (str): 'simplify' or '', default is 'simplify' which return only data points with values, if set to '', return all columns.
    missing_pct (float): a float number between 0 and 1, default is 0.8, which means remove all columns from df that have more than 80% missing values.
    """
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/finance/{symbol}/tooltip"
    response = requests.request("GET", url, headers=headers, data={}).json()
    df = json_normalize(response)
    df['ticker'] = symbol
    # move ticker column to the front
    cols = df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df = df[cols]
    # if mode = 'simplify', filter out all columns contain 'Name' in their values, otherwise if value set to '', return all columns
    if mode == 'simplify':
        df = df.loc[:,~df.columns.str.contains('Name')]
    # Remove all columns from df that have more than 80% missing values.
    df = df.loc[:, df.isnull().mean() < missing_pct]
    return df

def ticker_price_volatility (symbol='TCB', headers=tcbs_headers):
    """
    Return a DataFrame of ticker price volatility data.
    Parameters:
    ticker (str): ticker of the company, default is 'TCB', other tickers available can be obtained from the function `listing_companies()`.
    """
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/ticker/{symbol}/price-volatility"
    response = requests.request("GET", url, headers=headers, data={}).json()
    df = json_normalize(response)
    # add ticker_ as the prefix to all columns except ticker column
    df.columns = ['ticker_' + col if col != 'ticker' else col for col in df.columns]
    return df

def company_insider_deals (symbol='TCB', page_size=20, page=0, headers=tcbs_headers):
    """
    Return a DataFrame of company insider trading data.
    Parameters:
    ticker (str): ticker of the company, default is 'TCB', other tickers available can be obtained from the function `listing_companies()`.
    size (int): number of items per page, default is 20.
    page (int): page number, default is 0.
    """
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/company/{symbol}/insider-dealing?page={page}&size={page_size}"
    response = requests.request("GET", url, headers=headers, data={}).json()
    df = json_normalize(response['listInsiderDealing'])
    df.drop(columns=['no'], inplace=True)
    # rename columns anDate to dealAnnounceDate, dealingMethod to dealMethod, dealingAction to dealAction, quantity to dealQuantity, price to dealPrice, dealRatio
    df.rename(columns={'anDate': 'dealAnnounceDate', 'dealingMethod': 'dealMethod', 'dealingAction': 'dealAction', 'quantity': 'dealQuantity', 'price': 'dealPrice', 'ratio': 'dealRatio'}, inplace=True)
    # convert dealAnnounceDate column to datetime format, keep the same format as 'd/m/y'
    df['dealAnnounceDate'] = pd.to_datetime(df['dealAnnounceDate'], format='%d/%m/%y')
    # sort the DataFrame by dealAnnounceDate column
    df.sort_values(by='dealAnnounceDate', ascending=False, inplace=True)
    # replace value of dealMethod column, 1 with 'Cổ đông lớn', 2 with 'Cổ đông sáng lập', 0 with Cổ đông nội bộ
    df['dealMethod'].replace({1: 'Cổ đông lớn', 2: 'Cổ đông sáng lập', 0: 'Cổ đông nội bộ'}, inplace=True)
    # replace value of dealAction column, 1 with 'Bán', 0 with 'Mua'
    df['dealAction'].replace({'1': 'Bán', '0': 'Mua'}, inplace=True)
    return df


def company_subsidiaries_listing (symbol='TCB', page_size=100, page=0, headers=tcbs_headers):
    """
    Return a DataFrame of company subsidiaries data.
    Parameters:
    ticker (str): ticker of the company, default is 'TCB', other tickers available can be obtained from the function `listing_companies()`.
    size (int): number of items per page, maximum of 100.
    page (int): page number, default is 0. If the page_size is greater than 100, the function will automatically loop through the page number to get all the subsidiaries.
    """
    # If page_size is greater than 100, set it to 100, loop through the page number to get all the subsidiaries
    df_ls = []
    if page_size > 100:
        max_page = page_size // 100
        page_size = 100
        for page in range(max_page):
            # handling error in case of the page number and page_size are not valid
            try:
                url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/company/{symbol}/sub-companies?page={page}&size={page_size}"
                response = requests.request("GET", url, headers=tcbs_headers, data={}).json()
                df = json_normalize(response['listSubCompany'])
                df_ls.append(df)
            except:
                print(f'Error getting data from page {page}')
                # Write the error message and ticker list to a txt log file
                with open(f'{DB_APPDATA_PATH}/log/subsidiaries_error-{today}.txt', 'a') as f:
                        f.write(f'Error when getting subsidiaries data of {symbol} at page {page}\n')
                        f.close()
                continue
    else:
        url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/company/{symbol}/sub-companies?page={page}&size={page_size}"
        response = requests.request("GET", url, headers=headers, data={}).json()
        df = json_normalize(response['listSubCompany'])
        df_ls.append(df)
    # concat df_ls and reset index
    df = pd.concat(df_ls, ignore_index=True)
    df['ticker'] = symbol
    df.drop(columns=['no'], inplace=True)
    # rename companyName to subCompanyName, ownPercent to subCompanyOwnPercent
    df.rename(columns={'companyName': 'subCompanyName', 'ownPercent': 'subOwnPercent'}, inplace=True)
    return df


def company_officers (symbol='TCB', page_size=20, page=0, headers=tcbs_headers):
    """
    Return a DataFrame of company officers data.
    Parameters:
    ticker (str): ticker of the company, default is 'TCB', other tickers available can be obtained from the function `listing_companies()`.
    page_size (int): number of records per page, default is 20, can be increased to 100 or so.
    page (int): page number, default is 0.
    """
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/company/{symbol}/key-officers?page={page}&size={page_size}"
    response = requests.request("GET", url, headers=headers, data={}).json()
    df = json_normalize(response['listKeyOfficer'])
    df['ticker'] = symbol
    df.drop(columns=['no'], inplace=True)
    # rename companyName to subCompanyName, ownPercent to subCompanyOwnPercent
    df.rename(columns={'name': 'officerName', 'position': 'officerPosition', 'ownPercent':'officerOwnPercent'}, inplace=True)
    # sort by officerOwnPercent
    df.sort_values(by=['officerOwnPercent', 'officerPosition'], ascending=False, inplace=True)
    return df


def ticker_events (symbol='TPB', page_size=15, page=0, headers=tcbs_headers):
    """
    Return a DataFrame of ticker events data.
    Parameters:
    ticker (str): ticker of the company, default is 'TPB', other tickers available can be obtained from the function `listing_companies()`.
    page_size (int): number of records per page, default is 15, can be increased to 100 or so.
    page (int): page number, default is 0. You can increase the page number to get more events.
    """
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/ticker/{symbol}/events-news?page={page}&size={page_size}"
    response = requests.request("GET", url, headers=headers, data={}).json()
    df = pd.DataFrame(response['listEventNews'])
    return df

def ticker_news (symbol='TCB', page_size=15, page=0, headers=tcbs_headers):
    """
    Return a DataFrame of ticker news data.
    Parameters:
    ticker (str): ticker of the company, default is 'TCB', other tickers available can be obtained from the function `listing_companies()`.
    page_size (int): number of records per page, default is 15, can be increased to 100 or so.
    page (int): page number, default is 0. You can increase the page number to get more news.
    """
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/ticker/{symbol}/activity-news?page={page}&size={page_size}"
    response = requests.request("GET", url, headers=headers, data={}).json()
    df = pd.DataFrame(response['listActivityNews'])
    df['ticker'] = symbol
    return df