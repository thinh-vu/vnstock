from .config import *

# UTILS

def check_language_input(lang):
    """Check language input. Default to Vietnamese if the chosen language is not supported

    Parameters
    ----------
        lang : str
            language of the column label. Supported: 'vi' (default), 'en'
    
    Returns
    -------
        str
            supported language
    """
    supported_languages = {'en': 'English', 'vi': 'Tiếng Việt'}
    if lang.lower() not in supported_languages:
        print(f"Warning: Unsupported language '{lang}', defaulting to Vietnamese.")
        return 'vi'
    else:
        return lang.lower()

# MUTUAL FUNDS

def mutual_fund_listing(lang='vi', headers=fmarket_headers):
    """Retrieve list of available funds from Fmarket. Live data is retrieved from the Fmarket API.
    
    Parameters
    ----------
        lang: str
            language of the column label. Supported: 'vi' (default), 'en'
        headers: dict
            headers of the request
    
    Returns
    -------
        df: pd.DataFrame
            DataFrame of all available mutual fund listed on Fmarket.
    """
    # Check language input. Default to Vietnamese if the chosen language is not supported
    lang = check_language_input(lang)

    # API call
    payload = {
        "types": ["NEW_FUND", "TRADING_FUND"],
        "issuerIds": [],
        "sortOrder": "DESC",
        "sortField": "navTo6Months",
        "page": 1,
        "pageSize": 100,
        "isIpo": False,
        "fundAssetTypes": [],
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
            'shortName',
            'name',
            'owner.name',
            'dataFundAssetType.name',
            'managementFee',
            'productNavChange.navTo6Months',
            'nav',
            'code',
            'vsdFeeId',
            'id'
        ]
        df = df[column_subset]

        # sort by 'Fund manager' then by 'Fund short name'
        df = df.sort_values(by=['owner.name', 'shortName'], ascending=[False, True])
        
        # rename column label according to language choice
        language_mappings = {
            'vi': {
                'shortName': 'Tên viết tắt',
                'name': 'Tên Quỹ',
                'owner.name': 'Công ty Quản lý Quỹ',
                'dataFundAssetType.name': 'Loại Quỹ',
                'managementFee': 'Phí quản lý (%)',
                'productNavChange.navTo6Months': 'Lợi nhuận 6 tháng gần nhất (%)',
                'nav': 'Giá trị tài sản ròng/CCQ (VND)',
                'id': 'fund_id_fmarket'
            },
            'en': {
                'shortName': 'Fund short name',
                'name': 'Fund name',
                'owner.name': 'Fund manager',
                'dataFundAssetType.name': 'Fund type',
                'managementFee': 'Management fee (%)',
                'productNavChange.navTo6Months': '6-month annualized return (%)',
                'nav': 'NAV/Unit (VND)',
                'id': 'fund_id_fmarket'
            }
        }
        column_mapping = language_mappings[lang.lower()]
        df.rename(columns=column_mapping, inplace=True)
        
        # reset index column
        df = df.reset_index(drop=True)

        # output
        return df
    else:
        print(f"Error in API response {response.text}", "\n")

def mutual_fund_top_holdings(symbol=23, lang='vi', headers=fmarket_headers):
    """Retrieve list of top 10 holdings in the specified fund. Live data is retrieved from the Fmarket API.

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
        DataFrame of the current top 10 holdings of the selected fund.
    """
    # Check language input. Default to Vietnamese if the chosen language is not supported
    lang = check_language_input(lang)
    
    # API call
    # Logic: there are funds which allocate to either equities or fixed income securities, or both
    url = f"https://api.fmarket.vn/res/products/{symbol}"
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
            # Add new column 'fund_id_market'
            df_stock['fund_id_fmarket'] = str(symbol)
            # Calculate the sum for the 'netAssetPercent' column. Then append it as a new row
            df_stock.loc['Total', 'netAssetPercent'] = df_stock['netAssetPercent'].sum()
            # Fill NaN values with blank, only in the 'Total' row
            df_stock.loc['Total'] = df_stock.loc['Total'].fillna('')
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
            df_bond['fund_id_fmarket'] = str(symbol)
            df_bond.loc['Total', 'netAssetPercent'] = df_bond['netAssetPercent'].sum()
            df_bond.loc['Total'] = df_bond.loc['Total'].fillna('')
            df = pd.concat([df, df_bond])
        else:
            pass
        
        # rearrange columns to display
        column_subset = [
            'stockCode',
            'industry',
            'netAssetPercent',
            'type',
            'updateAt',
            'fund_id_fmarket'
        ]
        df = df[column_subset]

        # rename column label according to language choice
        language_mappings = {
            'vi': {
                'stockCode': 'Tên',
                'industry': 'Ngành',
                'netAssetPercent': '% Giá trị tài sản',
                'type': 'Loại tài sản',
                'updateAt': 'Cập nhật lúc'
            },
            'en': {
                'stockCode': 'Ticker',
                'industry': 'Sector',
                'netAssetPercent': '% NAV',
            }
        }
        column_mapping = language_mappings[lang.lower()]
        df.rename(columns=column_mapping, inplace=True)

        # output
        return df
    else:
        print(f"Error in API response {response.text}", "\n")

def mutual_fund_nav_report(symbol=23, lang='vi', headers=fmarket_headers):
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
    lang = check_language_input(lang)
        
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
