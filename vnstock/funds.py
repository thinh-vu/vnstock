from .config import *
from typing import List

# UTILS


def convert_unix_to_datetime(
    df_to_convert: pd.DataFrame, columns: List[str]
) -> pd.DataFrame:
    """Converts all the specified columns of a dataframe to date format and fill NaN for negative values."""
    df = df_to_convert.copy()
    for col in columns:
        df[col] = pd.to_datetime(
            df[col], unit="ms", utc=True, errors="coerce"
        ).dt.strftime("%Y-%m-%d")
        df[col] = df[col].where(df[col].ge("1970-01-01"))
    return df


# MUTUAL FUNDS


def funds_listing(fund_type="", headers=fmarket_headers) -> pd.DataFrame:
    """
    Retrieve list of available funds from Fmarket. Live data is retrieved from the Fmarket API. Visit https://fmarket.vn to learn more.

    Parameters
    ----------
        fund_type : str
            available fund types: "" (default), "BALANCED", "BOND", "STOCK"
        headers : dict
            headers of the request

    Returns
    -------
        df : pd.DataFrame
            DataFrame of all available mutual fund listed on Fmarket.
    """

    # Check fund_type input
    fund_type = fund_type.upper()
    fundAssetTypes = {
        "": [],
        "BALANCED": ["BALANCED"],
        "BOND": ["BOND"],
        "STOCK": ["STOCK"],
    }.get(fund_type, [])

    if fund_type not in {"", "BALANCED", "BOND", "STOCK"}:
        print(
            f"Warning: Unsupported fund type '{fund_type}', defaulting to all fund types."
        )

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
        "thirdAppIds": [],
    }
    url = "https://api.fmarket.vn/res/products/filter"
    response = requests.post(url, json=payload, headers=headers)
    status = response.status_code
    if status == 200:
        data = response.json()
        print(
            "Total number of funds currently listed on Fmarket: ", data["data"]["total"]
        )
        df = json_normalize(data, record_path=["data", "rows"])

        # select columns to display
        column_subset = [
            "shortName",
            "name",
            "dataFundAssetType.name",
            "owner.name",
            "managementFee",
            "firstIssueAt",
            "nav",
            "productNavChange.navToPrevious",
            "productNavChange.navToLastYear",
            "productNavChange.navToBeginning",
            "productNavChange.navTo1Months",
            "productNavChange.navTo3Months",
            "productNavChange.navTo6Months",
            "productNavChange.navTo12Months",
            "productNavChange.navTo24Months",
            "productNavChange.navTo36Months",
            "productNavChange.annualizedReturn36Months",
            "productNavChange.updateAt",
            "id",
            "code",
            "vsdFeeId",
        ]

        df = df[column_subset]

        # Convert Unix timestamp to date format
        df = convert_unix_to_datetime(
            df_to_convert=df, columns=["firstIssueAt", "productNavChange.updateAt"]
        )

        # sort by '36-month NAV change'
        df = df.sort_values(by="productNavChange.navTo36Months", ascending=False)

        # rename column label to snake_case
        column_mapping = {
            "shortName": "short_name",
            "name": "name",
            "dataFundAssetType.name": "fund_type",
            "owner.name": "fund_owner_name",
            "managementFee": "management_fee",
            "firstIssueAt": "inception_date",
            "nav": "nav",
            "productNavChange.navToPrevious": "nav_change_previous",
            "productNavChange.navToLastYear": "nav_change_last_year",
            "productNavChange.navToBeginning": "nav_change_inception",
            "productNavChange.navTo1Months": "nav_change_1m",
            "productNavChange.navTo3Months": "nav_change_3m",
            "productNavChange.navTo6Months": "nav_change_6m",
            "productNavChange.navTo12Months": "nav_change_12m",
            "productNavChange.navTo24Months": "nav_change_24m",
            "productNavChange.navTo36Months": "nav_change_36m",
            "productNavChange.annualizedReturn36Months": "nav_change_36m_annualized",
            "productNavChange.updateAt": "nav_update_at",
            "id": "fund_id_fmarket",
            "code": "fund_code",
            "vsdFeeId": "vsd_fee_id",
        }
        df.rename(columns=column_mapping, inplace=True)

        # reset index column
        df = df.reset_index(drop=True)

        return df
    else:
        raise requests.exceptions.HTTPError(
            f"Error in API response: {response.status_code} - {response.text}"
        )


def fund_details(
    symbol="SSISCA", type="top_holding_list", headers=fmarket_headers
) -> pd.DataFrame:
    """
    Retrieve fund details for a specific fund. Live data is retrieved from the Fmarket API.

    Parameters
    ----------
        symbol : str
            ticker of a fund. A.k.a fund short name
        type : str
            type of data to retrieve. Options: 'top_holding_list' (default), 'industry_holding_list', 'nav_report', 'asset_holding_list'
        headers : dict
            headers of the request. Options: fmaker_headers (default)

    Returns
    -------
        df : pd.DataFrame
            DataFrame of the current top holdings of the selected fund.
    """

    # validate "symbol" param input
    symbol = symbol.upper()
    try:
        # Lookup a valid "fundID" related to "symbol"
        # invalid symbol exception will be handled in fund_filter()
        fundID = int(fund_filter(symbol)["id"][0])
        print(f"Retrieving data for {symbol}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e

    # validate "type" param input
    type_mappings = {
        "top_holding_list": fund_top_holding,
        "industry_holding_list": fund_industry_holding,
        "nav_report": fund_nav_report,
        "asset_holding_list": fund_asset_holding,
    }

    if type in type_mappings:
        # Match with appropriate function
        df = type_mappings[type](fundId=fundID, headers=headers)
        df["short_name"] = symbol
        return df
    else:
        print(
            f"Error: {type} is not a valid input.\n"
            f"4 current options are:\n"
            f"top_holding_list\n"
            f"industry_holding_list\n"
            f"nav_report\n"
            f"asset_holding_list"
        )
        raise ValueError


def fund_filter(symbol="", headers=fmarket_headers) -> pd.DataFrame:
    """Filter FundID based on Fund short name

    Parameters
    ----------
        symbol : str
            Fund short name. Empty string by default to list all available fund short name and their FundID
        headers : dict
            headers of API request. Options: fmarket_headers (default)

    Returns
    -------
        df : pd.DataFrame
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
    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        df = json_normalize(data, record_path=["data", "rows"])
        if not df.empty:
            # retrieve only column_subset
            column_subset = ["id", "shortName"]
            df = df[column_subset]
            return df
        else:
            raise ValueError(
                f"No fund found with this symbol {symbol}.\n"
                f"See funds_listing() for the list of valid Fund short names."
            )
    else:
        raise requests.exceptions.HTTPError(
            f"Error in API response: {response.status_code} - {response.text}"
        )


def fund_top_holding(fundId=23, headers=fmarket_headers) -> pd.DataFrame:
    """
    Retrieve list of top 10 holdings in the specified fund. Live data is retrieved from the Fmarket API.

    Parameters
    ----------
        fundId : int
            id of a fund in fmarket database
        headers : dict
            headers of the request. Options: fmaker_headers (default)

    Returns
    -------
        df : pd.DataFrame
            DataFrame of the current top 10 holdings of the selected fund.
    """

    # API call
    # Logic: there are funds which allocate to either equities or fixed income securities, or both
    url = f"https://api.fmarket.vn/res/products/{fundId}"
    response = requests.get(url, headers=headers, cookies=None)
    status = response.status_code
    if status == 200:
        data = response.json()
        df = pd.DataFrame()

        # Flatten top holding equities
        df_stock = json_normalize(data, record_path=["data", "productTopHoldingList"])
        if not df_stock.empty:
            # Convert unix timestamp into date format
            df_stock = convert_unix_to_datetime(
                df_to_convert=df_stock, columns=["updateAt"]
            )
            # Merge to output
            df = pd.concat([df, df_stock])

        # Flatten top holding fixed income securities
        df_bond = json_normalize(
            data, record_path=["data", "productTopHoldingBondList"]
        )
        if not df_bond.empty:
            df_bond = convert_unix_to_datetime(
                df_to_convert=df_bond, columns=["updateAt"]
            )
            df = pd.concat([df, df_bond])

        # if df is not empty, then rearrange and return df as output
        if not df.empty:
            df["fundId"] = int(fundId)
            # rearrange columns to display
            column_subset = [
                "stockCode",
                "industry",
                "netAssetPercent",
                "type",
                "updateAt",
                "fundId",
            ]
            df = df[column_subset]

            # rename column label to snake_case
            column_mapping = {
                "stockCode": "stock_code",
                "industry": "industry",
                "netAssetPercent": "net_asset_percent",
                "type": "type_asset",
                "updateAt": "update_at",
            }
            df.rename(columns=column_mapping, inplace=True)

            return df
        else:
            print(f"Warning: No data available for fundId {fundId}.")
            return pd.DataFrame()
    else:
        # invalid fundId error is 400 from api
        raise requests.exceptions.HTTPError(
            f"Error in API response: {response.status_code} - {response.text}"
        )


def fund_industry_holding(fundId=23, headers=fmarket_headers) -> pd.DataFrame:
    """Retrieve list of industries and fund distribution for specific fundID. Live data is retrieved from the Fmarket API.

    Parameters
    ----------
        fundId : int
            id of a fund in fmarket database
        headers : dict
            headers of the request. Options: fmaker_headers (default)

    Returns
    -------
        df : pd.DataFrame
            DataFrame of the current top industries in the selected fund.
    """

    # API call
    url = f"https://api.fmarket.vn/res/products/{fundId}"
    response = requests.get(url, headers=headers, cookies=None)

    if response.status_code == 200:
        data = response.json()
        df = json_normalize(data, record_path=["data", "productIndustriesHoldingList"])

        # rearrange columns to display
        column_subset = [
            "industry",
            "assetPercent",
        ]
        df = df[column_subset]

        # rename column label to snake_case
        columns_mapping = {
            "industry": "industry",
            "assetPercent": "net_asset_percent",
        }
        df.rename(columns=columns_mapping, inplace=True)

        return df
    else:
        # invalid fundId error is 400 from api
        raise requests.exceptions.HTTPError(
            f"Error in API response: {response.status_code} - {response.text}"
        )


def fund_nav_report(fundId=23, headers=fmarket_headers) -> pd.DataFrame:
    """Retrieve all available daily NAV data point of the specified fund. Live data is retrieved from the Fmarket API.

    Parameters
    ----------
        fundId : int
            id of a fund in fmarket database.
        headers : dict
            headers of the request. Default is fmaker_headers

    Returns
    -------
        df : pd.DataFrame
            DataFrame of all avalaible daily NAV data points of the selected fund.
    """

    # API call
    # Set the date range to the current date
    current_date = datetime.now().strftime("%Y%m%d")
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
        df = json_normalize(data, record_path=["data"])

        if not df.empty:
            # rearrange columns to display
            column_subset = ["navDate", "nav"]
            df = df[column_subset]

            # rename column label to snake_case
            column_mapping = {
                "navDate": "date",
                "nav": "nav_per_unit",
            }
            df.rename(columns=column_mapping, inplace=True)

            return df
        else:
            raise ValueError(f"No data with this fund_id {fundId}")
    else:
        raise requests.exceptions.HTTPError(
            f"Error in API response: {response.status_code} - {response.text}"
        )


def fund_asset_holding(fundId=23, headers=fmarket_headers) -> pd.DataFrame:
    """Retrieve list of assets holding allocation for specific fundID. Live data is retrieved from the Fmarket API.

    Parameters
    ----------
        fundId : int
            id of a fund in fmarket database.
        headers : dict
            headers of the request. Default is fmaker_headers

    Returns
    -------
        df : pd.DataFrame
            DataFrame of assets holding allocation of the selected fund.
    """

    # API call
    url = f"https://api.fmarket.vn/res/products/{fundId}"
    response = requests.get(url, headers=headers, cookies=None)
    if response.status_code == 200:
        data = response.json()
        df = json_normalize(data, record_path=["data", "productAssetHoldingList"])

        # rearrange columns to display
        column_subset = [
            "assetPercent",
            "assetType.name",
        ]
        df = df[column_subset]

        # rename column label to snake_case
        column_mapping = {
            "assetPercent": "asset_percent",
            "assetType.name": "asset_type",
        }
        df.rename(columns=column_mapping, inplace=True)

        return df
    else:
        # invalid fundId error is 400 from api
        raise requests.exceptions.HTTPError(
            f"Error in API response: {response.status_code} - {response.text}"
        )
