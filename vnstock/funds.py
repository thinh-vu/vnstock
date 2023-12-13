from .config import *

# UTILS

def convert_unix_to_datetime(
        df_to_convert: pd.DataFrame, columns: list[str]
) -> pd.DataFrame:
    """Converts all the specified columns of a dataframe to date format and fill NaN for negative values."""
    df = df_to_convert.copy()
    for col in columns:
        df[col] = pd.to_datetime(df[col], unit='ms', utc=True, errors='coerce').dt.strftime('%Y-%m-%d')
        df[col] = df[col].where(df[col].ge('1970-01-01'))
    return df

def check_language_input(lang):
    """Check language input. Default to Vietnamese if not supported"""
    supported_languages = {'en': 'English', 'vi': 'Tiếng Việt'}
    if lang.lower() not in supported_languages:
        print(f"Warning: Unsupported language '{lang}', defaulting to Vietnamese.")
        return 'vi'
    else:
        return lang.lower()

# MUTUAL FUNDS

def funds_listing(lang='vi', fund_type="", mode="simplify", decor=True, headers=fmarket_headers):
    """
    Retrieve list of available funds from Fmarket. Live data is retrieved from the Fmarket API. Visit https://fmarket.vn to learn more.
    
    Parameters
    ----------
        lang: str
            language of the column label. Options: 'vi' (default), 'en'
        fund_type: list
            available fund types: "" (default), "BALANCED", "BOND", "STOCK"
        mode: str
            return only important columns or all available info. Options: "simplify" (default), "full"
        decor: bool
            transform column label to Title Case. Options: True (default), False
        headers: dict
            headers of the request
    
    Returns
    -------
        df: pd.DataFrame
            DataFrame of all available mutual fund listed on Fmarket.
    """
    # Check language input. Default to Vietnamese if the chosen language is not supported
    lang = check_language_input(lang)
    
    # Check fund_type input
    fundAssetTypes = {
        "": [],
        "BALANCED": ["BALANCED"],
        "BOND": ["BOND"],
        "STOCK": ["STOCK"]
    }.get(fund_type, [])
        
    if fund_type not in ["", "BALANCED", "BOND", "STOCK"]:
        print(f"Warning: Unsupported fund type '{fund_type}', defaulting to all fund types.")

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
        column_subset_full = [
            'id',
            'shortName',
            'name',
            'dataFundAssetType.name',
            'owner.name',
            'managementFee',
            'firstIssueAt',
            'productNavChange.navToPrevious',
            'productNavChange.navToLastYear',
            'productNavChange.navToBeginning',
            'productNavChange.navTo1Months',
            'productNavChange.navTo3Months',
            'productNavChange.navTo6Months',
            'productNavChange.navTo12Months',
            'productNavChange.navTo24Months',
            'productNavChange.navTo36Months',
            'productNavChange.annualizedReturn36Months',
            'productNavChange.updateAt',
            'nav',
            'code',
            'vsdFeeId',
        ]
        column_subset_simplified = [
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
        ]
        # choose column_subset based on user input param "mode"
        column_subsets = {
            "simplify": column_subset_simplified,
            "full": column_subset_full
        }
        df = df[column_subsets.get(mode, column_subset_simplified)]

        # Convert Unix timestamp to date format
        if mode == "full":
            df = convert_unix_to_datetime(
                df_to_convert=df,
                columns=[
                    'firstIssueAt', 
                    'productNavChange.updateAt'
                    ]
                )

        # set data type for columns, id to int
        df = df.astype({'id': 'int'})

        # sort by '36-month NAV change'
        df = df.sort_values(by='productNavChange.navTo36Months', ascending=False)
        
        # rename column label according to language choice
        language_mappings = {
            'vi': {
                'id': 'fundId',
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
                'id': 'fundId'
            }
        }
        if decor==True:
            column_mapping = language_mappings[lang.lower()]
            df.rename(columns=column_mapping, inplace=True)
        
        # reset index column
        df = df.reset_index(drop=True)
        # output                                                                                                            
        return df
    else:                               
        print(f"Error in API response {response.text}", "\n")

def fund_details (symbol='SSISCA', type='top_holding_list', headers=fmarket_headers) -> pd.DataFrame:
    """
    Retrieve fund details for a specific fund. Live data is retrieved from the Fmarket API.

    Parameters
    ----------
        symbol: str
            ticker of a fund. A.k.a fund short name
        type: str
            type of data to retrieve. Options: 'top_holding_list' (default), 'industry_holding_list', 'nav_report', 'asset_holding_list'
        headers: dict
            headers of the request. Options: fmaker_headers (default)

    Returns
    -------
        df: pd.DataFrame
            DataFrame of the current top holdings of the selected fund.
    """
    # validate "symbol" user input
    symbol = symbol.upper()
    try:
        # Lookup a valid "fundID" related to "symbol"
        fundID = int(fund_filter(symbol)['id'][0])
        print(f'Retrieving data for {symbol}')
    except KeyError as e:
        print(f'Error: Unable to retrieve data for this fund {symbol}.\n'
              f'See funds_listing() for the list of valid Fund short names.')
        raise e
    except Exception as e:
        print(f'An unexpected error occurred.', e)
    
    # validate "type" user input
    type_mappings = {
        'top_holding_list': fund_top_holding,
        'industry_holding_list': fund_industry_holding,
        'nav_report': fund_nav_report,
        'asset_holding_list': fund_asset_holding
    }

    if type in type_mappings:
        # Match with appropriate function
        df = type_mappings[type](fundId=fundID, lang='vi', headers=headers)
        df['shortName'] = symbol
    else:
        print(f'Error: {type} is not a valid input.\n'
              f'4 current options are:\n'
              f'top_holding_list\n'
              f'industry_holding_list\n'
              f'nav_report\n'
              f'asset_holding_list')

    return df

def fund_filter(symbol="", headers=fmarket_headers) -> pd.DataFrame:
    """Filter FundID based on Fund short name

    Parameters
    ----------
        symbol: str
            Fund short name. Empty string by default to list all available funds
        headers: dict
            headers of API request. Options: fmarket_headers (default)
    
    Returns
    -------
        df: pd.DataFrame
            DataFrame of filtered funds
    """
    symbol = symbol.upper()
    payload = {
        "searchField": symbol,
        "types": ["NEW_FUND", "TRADING_FUND"],
        "pageSize": 100,
        }
    url = "https://api.fmarket.vn/res/products/filter"
    payload = json.dumps(payload)
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        df = json_normalize(data, record_path=['data', 'rows'])
        # retrieve only column_subset
        column_subset=['id', 'shortName']
        df = df[column_subset]
        return df
    else:
        raise ValueError(f"Error in API response.\n{response.text}")

def fund_top_holding(fundId=23, lang='vi', headers=fmarket_headers) -> pd.DataFrame:
    """
    Retrieve list of top 10 holdings in the specified fund. Live data is retrieved from the Fmarket API.
    
    Parameters
    ----------
        fundId: int
            id of a fund in fmarket database
        lang: str
            language of the column label. Options: 'vi' (default), 'en'
        headers: dict
            headers of the request. Options: fmaker_headers (default)
    
    Returns
    -------
        df: pd.DataFrame
            DataFrame of the current top 10 holdings of the selected fund.
    """
    # Check language input. Default to Vietnamese if the chosen language is not supported
    lang = check_language_input(lang)

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
            df_stock = convert_unix_to_datetime(df_to_convert=df_stock, columns=["updateAt"])
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
            df_bond = convert_unix_to_datetime(df_to_convert=df_bond, columns=["updateAt"])
            df = pd.concat([df, df_bond])
        else:
            pass
        
        # if df is not empty, then go ahead
        if not df.empty:
            df['fundId'] = int(fundId)
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
        raise ValueError(f"Error in API response.\n{response.text}")


def fund_industry_holding (fundId=23, lang='vi', headers=fmarket_headers):
    """
    Retrieve list of industries and fund distribution for specific fundID. Live data is retrieved from the Fmarket API.
    """
    # Check language input. Default to Vietnamese if the chosen language is not supported
    lang = check_language_input(lang)

    # API call
    # Logic: there are funds which allocate to either equities or fixed income securities, or both
    url = f"https://api.fmarket.vn/res/products/{fundId}"
    response = requests.get(url, headers=headers, cookies=None)
    if response.status_code == 200:
        data = response.json()
        df = json_normalize(data, record_path=['data', 'productIndustriesHoldingList'])
        # drop id column
        try:
            df.drop(columns=['id'], inplace=True)
        except:
            pass
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


def fund_nav_report(fundId='23', lang='vi', headers=fmarket_headers) -> pd.DataFrame:
    """Retrieve all available daily NAV data point of the specified fund. Live data is retrieved from the Fmarket API.

    Parameters
    ----------
        symbol: int
            id of a fund in fmarket database. Retrieved from the 'fundId' column by calling the function mutual_fund_listing()
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
    lang = check_language_input(lang)

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
                'productId': 'fundId'
            },
            'en': {
                'navDate': 'Date',
                'nav': 'NAV/Unit (VND)',
                'productId': 'fundId'
            }
        }
        column_mapping = language_mappings[lang.lower()]
        df.rename(columns=column_mapping, inplace=True)

        # output
        return df
    else:
        raise ValueError(f"Error in API response.\n{response.text}")


def fund_asset_holding (fundId=23, lang='vi', headers=fmarket_headers):
    """
    Retrieve list of assets holding allocation for specific fundID. Live data is retrieved from the Fmarket API.
    """
    # Check language input. Default to Vietnamese if the chosen language is not supported
    lang = check_language_input(lang)

    # API call
    # Logic: there are funds which allocate to either equities or fixed income securities, or both
    url = f"https://api.fmarket.vn/res/products/{fundId}"
    response = requests.get(url, headers=headers, cookies=None)
    if response.status_code == 200:
        data = response.json()
        df = json_normalize(data, record_path=['data', 'productAssetHoldingList'])
        try:
            # drop id column
            df.drop(columns=['id', 'assetType.id', 'assetType.code', 'assetType.colorCode', 'createAt'], inplace=True)
            # convert updateAt to YYYY-mm-dd format
            df['updateAt'] = pd.to_datetime(df['updateAt'], unit='ms', utc=True).dt.strftime('%Y-%m-%d')
        except:
            pass
        columns_mapping = {'vi': {
                            'assetPercent': 'Tỉ trọng',
                            'assetType.name': 'Loại tài sản',
                            },
                            'en': {
                            'assetPercent': 'assetPercent',
                            'assetType.name': 'assetType',
                            }
                            }
        df.rename(columns=columns_mapping[lang.lower()], inplace=True)
        return df
    else:
        print(f"Error in API response {response.text}", "\n")