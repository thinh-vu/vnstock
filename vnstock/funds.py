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
                'owner.name': 'Fund manager',
                'dataFundAssetType.name': 'Fund type',
                'managementFee': 'Management fee (%)',
                'productNavChange.navTo6Months': '6-month annualized return (%)',
                'productNavChange.navTo36Months': '3-year annualized return (%)',
                'nav': 'NAV/Unit (VND)',
                'id': 'fund_id'
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

