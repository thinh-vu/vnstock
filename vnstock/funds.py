from .config import *

# MUTUAL FUNDS

def funds_listing(lang='vi', fund_type="", headers=fmarket_headers):
    """
    Retrieve list of available funds from Fmarket. Live data is retrieved from the Fmarket. Visit https://fmarket.vn to learn more.
    
    Parameters
    ----------
        lang: str
            language of the column label. Supported: 'vi' (default), 'en'
        fund_type: list
        headers: dict
            headers of the request
    
    Returns
    -------
        df: pd.DataFrame
            DataFrame of all available mutual fund listed on Fmarket.
    """
    # Check language input. Default to Vietnamese if the chosen language is not supported
    supported_languages = {'en': 'English', 'vi': 'Tiếng Việt'}
    if lang.lower() not in supported_languages:
        print(f"Warning: Unsupported language '{lang}', defaulting to Vietnamese.")
        lang = 'vi'

    if fund_type == "":
        fundAssetTypes = []
    elif fund_type == "BALANCED":
        fundAssetTypes = ["BALANCED"]
    elif fund_type == "BOND":
        fundAssetTypes = ["BOND"]
    elif fund_type == "STOCK":
        fundAssetTypes = ["STOCK"]
    else:
        print(f"Error: Unsupported fund type '{fund_type}', defaulting to all funds.")
        fundAssetTypes = []

    # API call
    payload = {
        "types": ["NEW_FUND", "TRADING_FUND"],
        "issuerIds": [],
        "sortOrder": "DESC",
        "sortField": "navTo6Months",
        "page": 1,
        "pageSize": 100,
        "isIpo": False,
        "fundAssetTypes": fundAssetTypes,
        "bondRemainPeriods": [],
        "searchField": "",
        "isBuyByReward": False,
        "thirdAppIds": []
    }
    url = "https://api.fmarket.vn/res/products/filter"
    response = requests.post(url, json=payload, headers=headers)
    status = response.status_code
    if status == 200:
        data = response.json()
        print('Total number of funds currently listed on Fmarket: ', data['data']['total'])
        df = json_normalize(data, record_path=['data', 'rows'])

        # rearrange columns to display
        column_subset = [
            'id',
            'shortName',
            'name',
            'dataFundAssetType.name',
            'owner.name',
            'managementFee',
            'productNavChange.navTo6Months',
            'productNavChange.navTo36Months',
            'nav',
            'code',
            'vsdFeeId'
        ]
        df = df[column_subset]

        # sort by 'Fund manager' then by 'Fund short name'
        # df = df.sort_values(by=['owner.name', 'shortName'], ascending=[False, True])
        df = df.sort_values(by='productNavChange.navTo36Months', ascending=False)
        
        # rename column label according to language choice
        language_mappings = {
            'vi': {
                'id': 'fund_id',
                'shortName': 'Tên viết tắt',
                'name': 'Tên CCQ',
                'dataFundAssetType.name': 'Loại Quỹ',
                'owner.name': 'Tổ chức phát hành',
                'managementFee': 'Phí quản lý (%)',
                'productNavChange.navTo6Months': 'Lợi nhuận 6 tháng gần nhất (%)',
                'productNavChange.navTo36Months': 'Lợi nhuận 3 năm gần nhất (%)',
                'nav': 'Giá gần nhất'
            },
            'en': {
                'shortName': 'Fund short name',
                'name': 'Fund name',
                'owner.name': 'Fund owner',
                'dataFundAssetType.name': 'Fund asset type',
                'managementFee': 'Management fee (%)',                                           
                'productNavChange.navTo6Months': '6-month NAV change (%)',
                'productNavChange.navTo36Months': '3-year NAV change (%)',
                'nav': 'NAV/Unit (VND)',
                'id': 'fund_id'
            }
        }
        column_mapping = language_mappings[lang.lower()]
        # set data type for columns, id to object
        df = df.astype({'id': 'object'})
        df.rename(columns=column_mapping, inplace=True)
        
        # reset index column
        df = df.reset_index(drop=True)
        # output                                                                                                            
        return df
    else:                               
        print(f"Error in API response {response.text}", "\n")

def fund_details (symbol='SSISCA', type='top_holding_list', headers=fmarket_headers):
    """
    Retrieve fund details for a specific fund. Live data is retrieved from the Fmarket API.
    Parameters:
        symbol (str): ticker of a fund
        type (str): type of data to retrieve. Default is 'top_holding_list', other options are 'industry_holding_list'
        headers (dict): headers of the request. Default is fmaker_headers
    Returns:
        df (pd.DataFrame): DataFrame of the current top holdings of the selected fund.
    """
    # get fundID from symbol using fund_filter
    fundID = fund_filter (payload={"searchField": symbol, "pageSize": 1, "types": ["NEW_FUND", "TRADING_FUND"]})['id']
    print(f'Getting data for {symbol}')
    if type == 'top_holding_list':
        df = fund_top_holding(fundId=23, lang='vi', headers=headers)
    elif type == 'industry_holding_list':
        df = fund_industry_holding(fundId=23, lang='vi', headers=headers)
    else:
        print('Please specify type of data to retrieve.')
    try:
        df['symbol'] = symbol
    except:
        pass
    return df

# payload = {
#   "types": [
#     "NEW_FUND",
#     "TRADING_FUND"
#   ],
#   "issuerIds": [],
#   "sortOrder": "DESC",
#   "sortField": "annualizedReturn36Months",
#   "page": 1,
#   "pageSize": 100,
#   "isIpo": False,
#   "fundAssetTypes": [],
#   "bondRemainPeriods": [],
#   "searchField": "VESAF",
#   "isBuyByReward": False,
#   "thirdAppIds": []
# }

def fund_filter (payload={"types": ["NEW_FUND", "TRADING_FUND"], "pageSize": 100, "searchField": "VESAF"}, columns=['id', 'shortName', 'name', 'description'], headers=fmarket_headers):
  url = "https://api.fmarket.vn/res/products/filter"
  payload = json.dumps(payload)
  response = requests.request("POST", url, headers=headers, data=payload)
  if response.status_code == 200:
    data = response.json()
    df = json_normalize(data, record_path=['data', 'rows'])
    # subset df to get only the columns in column_subset
    df = df[columns]
    return df

def fund_top_holding(fundId=23, lang='vi', headers=fmarket_headers):
    """
    Retrieve list of top 10 holdings in the specified fund. Live data is retrieved from the Fmarket API.
    
    Parameters
    ----------
        fundId (int): id of a fund in fmarket database. Retrieved from the 'fundId_fmarket' column by calling the function mutual_fund_listing()
        lang (str): language of the column label. Supported: 'vi' (default), 'en'
        headers (dict): headers of the request. Default is fmaker_headers
    
    Returns
    -------
    df (pd.DataFrame): DataFrame of the current top 10 holdings of the selected fund.
    """
    # Check language input. Default to Vietnamese if the chosen language is not supported
    supported_languages = {'en': 'English', 'vi': 'Tiếng Việt'}
    if lang.lower() not in supported_languages:
        print(f"Warning: Unsupported language '{lang}', defaulting to Vietnamese.")
        lang = 'vi'

    # API call
    # Logic: there are funds which allocate to either equities or fixed income securities, or both
    url = f"https://api.fmarket.vn/res/products/{fundId}"
    response = requests.get(url, headers=headers, cookies=None)
    status = response.status_code
    if status == 200:
        data = response.json()
        df = pd.DataFrame()

        # Flatten top holding equities
        df_stock = json_normalize(
            data, 
            record_path=['data', 'productTopHoldingList']
            )
        if not df_stock.empty:
            # Convert unix timestamp into date format
            df_stock['updateAt'] = pd.to_datetime(df_stock['updateAt'], unit='ms', utc=True).dt.strftime('%Y-%m-%d')
            # Merge to output
            df = pd.concat([df, df_stock])
        else:
            pass

        # Flatten top holding fixed income securities
        df_bond = json_normalize(
            data, 
            record_path=['data', 'productTopHoldingBondList']
            )
        if not df_bond.empty:
            df_bond['updateAt'] = pd.to_datetime(df_bond['updateAt'], unit='ms', utc=True).dt.strftime('%Y-%m-%d')
            df = pd.concat([df, df_bond])
        else:
            pass
        
        # if df is not empty, then go ahead
        if not df.empty:
            df['fundId'] = str(fundId)
            # rearrange columns to display
            column_subset = [
                'stockCode',
                'industry',
                'netAssetPercent',
                'type',
                'updateAt',
                'fundId'
            ]
            df = df[column_subset]

            # rename column label according to language choice
            language_mappings = {
                'vi': {
                    'stockCode': 'Tên',
                    'industry': 'Ngành',
                    'netAssetPercent': '% Giá trị tài sản',
                    'type': 'Loại tài sản',
                    'updateAt': 'Cập nhật lần cuối',
                },
                'en': {
                    'stockCode': 'Stock code',
                    'industry': 'Industry',
                    'netAssetPercent': '% NAV',
                }
            }
            column_mapping = language_mappings[lang.lower()]
            df.rename(columns=column_mapping, inplace=True)

            # output
            return df
        else:
            print(f"Warning: No data available for fundId {fundId}.")
            return None
    else:
        print(f"Error in API response {response.text}", "\n")


def fund_industry_holding (fundId=23, lang='vi', headers=fmarket_headers):
    """
    Retrieve list of industries and fund distribution for specific fundID. Live data is retrieved from the Fmarket API.
    """
    # Check language input. Default to Vietnamese if the chosen language is not supported
    supported_languages = {'en': 'English', 'vi': 'Tiếng Việt'}
    if lang.lower() not in supported_languages:
        print(f"Warning: Unsupported language '{lang}', defaulting to Vietnamese.")
        lang = 'vi'

    # API call
    # Logic: there are funds which allocate to either equities or fixed income securities, or both
    url = f"https://api.fmarket.vn/res/products/{fundId}"
    response = requests.get(url, headers=headers, cookies=None)
    if response.status_code == 200:
        data = response.json()
        df = json_normalize(data, record_path=['data', 'productIndustriesHoldingList'])
        # drop id column
        df.drop(columns=['id'], inplace=True)
        columns_mapping = {'vi': {
                            'industry': 'Ngành',
                            'assetPercent': '% Giá trị tài sản',
                            },
                            'en': {
                            'industry': 'Industry',
                            'assetPercent': '% NAV',
                            }
                            }
        df.rename(columns=columns_mapping[lang.lower()], inplace=True)
        return df
    else:
        print(f"Error in API response {response.text}", "\n")


def fund_nav_report(symbol=23, lang='vi', headers=fmarket_headers):
    """Retrieve all available daily NAV data point of the specified fund. Live data is retrieved from the Fmarket API.
    Parameters
    ----------
        symbol: int
            id of a fund in fmarket database. Retrieved from the 'fund_id_fmarket' column by calling the function mutual_fund_listing()
        lang: str
            language of the column label. Supported: 'vi' (default), 'en'
        headers: dict
            headers of the request. Default is fmaker_headers
    
    Returns
    -------
        df: pd.DataFrame
            DataFrame of all avalaible daily NAV data points of the selected fund.
    """
    # Check language input. Default to Vietnamese if the chosen language is not supported
    supported_languages = {'en': 'English', 'vi': 'Tiếng Việt'}
    if lang.lower() not in supported_languages:
        print(f"Warning: Unsupported language '{lang}', defaulting to Vietnamese.")
        lang = 'vi'

    # API call
    # Get the current date and format it as 'yyyyMMdd'
    current_date = datetime.now().strftime('%Y%m%d')
    url = "https://api.fmarket.vn/res/product/get-nav-history"
    payload = {
        "isAllData": 1,
        "productId": symbol,
        "fromDate": None,
        "toDate": current_date,
    }
    response = requests.post(url, json=payload, headers=fmarket_headers)
    status = response.status_code
    if status == 200:
        data = response.json()
        df = json_normalize(
            data, 
            record_path=['data']
            )

        # rearrange columns to display
        column_subset = [
            'navDate',
            'nav',
            'productId'
        ]
        df = df[column_subset]

        # rename column label according to language choice
        language_mappings = {
            'vi': {
                'navDate': 'Ngày',
                'nav': 'Giá trị tài sản ròng/CCQ (VND)',
                'productId': 'fund_id_fmarket'
            },
            'en': {
                'navDate': 'Date',
                'nav': 'NAV/Unit (VND)',
                'productId': 'fund_id_fmarket'
            }
        }
        column_mapping = language_mappings[lang.lower()]
        df.rename(columns=column_mapping, inplace=True)

        # output
        return df
    else:
        print(f"Error in API response {response.text}", "\n")


def fund_nav_report(symbol='VESAF', lang='vi', headers=fmarket_headers):
    """Retrieve all available daily NAV data point of the specified fund. Live data is retrieved from the Fmarket API.
    Parameters
    ----------
        symbol: int
            id of a fund in fmarket database. Retrieved from the 'fund_id_fmarket' column by calling the function mutual_fund_listing()
        lang: str
            language of the column label. Supported: 'vi' (default), 'en'
        headers: dict
            headers of the request. Default is fmaker_headers
    
    Returns
    -------
        df: pd.DataFrame
            DataFrame of all avalaible daily NAV data points of the selected fund.
    """
    fundId = str(fund_filter (payload={"searchField": symbol, "pageSize": 1, "types": ["NEW_FUND", "TRADING_FUND"]})['id'][0])
    # Check language input. Default to Vietnamese if the chosen language is not supported
    supported_languages = {'en': 'English', 'vi': 'Tiếng Việt'}
    if lang.lower() not in supported_languages:
        print(f"Warning: Unsupported language '{lang}', defaulting to Vietnamese.")
        lang = 'vi'

    # API call
    # Get the current date and format it as 'yyyyMMdd'
    current_date = datetime.now().strftime('%Y%m%d')
    url = "https://api.fmarket.vn/res/product/get-nav-history"
    payload = {
        "isAllData": 1,
        "productId": fundId,
        "fromDate": None,
        "toDate": current_date,
    }
    response = requests.post(url, json=payload, headers=fmarket_headers)
    status = response.status_code
    if status == 200:
        data = response.json()
        df = json_normalize(
            data, 
            record_path=['data']
            )

        # rearrange columns to display
        column_subset = [
            'navDate',
            'nav',
            'productId'
        ]
        df = df[column_subset]

        # rename column label according to language choice
        language_mappings = {
            'vi': {
                'navDate': 'Ngày',
                'nav': 'Giá trị tài sản ròng/CCQ (VND)',
                'productId': 'fund_id_fmarket'
            },
            'en': {
                'navDate': 'Date',
                'nav': 'NAV/Unit (VND)',
                'productId': 'fund_id_fmarket'
            }
        }
        column_mapping = language_mappings[lang.lower()]
        df.rename(columns=column_mapping, inplace=True)

        # output
        return df
    else:
        print(f"Error in API response {response.text}", "\n")