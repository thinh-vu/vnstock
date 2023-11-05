# DNSE API: https://www.dnse.vn
from .config import *

import requests
import json
import pandas as pd
from pandas import json_normalize

class DNSEClient:
    def __init__(self):
        self.token = None
        self.trading_token = None

    def login(self, user_name, password):
        """
        Authenticate the user and obtain a JWT token for further API requests.

        Args:
            user_name (str): DNSE username. Can be 064CXXXXX, your email, or your phone number.
            password (str): Your DNSE password.

        Returns:
            str: JWT token if authentication is successful, None otherwise.
        """
        url = "https://services.entrade.com.vn/dnse-user-service/api/auth"
        payload = json.dumps({'username': user_name, 'password': password})
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=payload)
        status = response.status_code
        if status == 200:
            print('Login successfully')
            self.token = response.json()['token']
            return self.token
        else:
            print('Login failed')
            return None

    def account(self):
        """
        Get the full user profile from DNSE.

        Returns:
            DataFrame: A DataFrame containing the user profile if successful, None otherwise.
        """
        url = "https://services.entrade.com.vn/dnse-user-service/api/me"
        payload = "N/A"
        headers = {
            'Content-Type': 'text/plain',
            'Authorization': f'Bearer {self.token}'
        }
        response = requests.get(url, headers=headers, data=payload)
        status = response.status_code
        if status == 200:
            print('Get profile successfully')
            df = pd.DataFrame(response.json(), index=[0])
            return df
        else:
            print('Get profile failed')
            return None

    def sub_accounts(self):
        """
        Get sub-accounts information.

        Returns:
            DataFrame: A DataFrame containing the sub-accounts information if successful, None otherwise.
        """
        url = "https://services.entrade.com.vn/dnse-order-service/accounts"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            df = json_normalize(result['accounts'])
            return df
        else:
            print("Error:", response.text)

    def account_balance (self, sub_account):
        """
        Get account balance for a specific sub-account.

        Args:
            sub_account (str): DNSE sub account number (mã tiểu khoản).
        """
        url = f"https://services.entrade.com.vn/dnse-order-service/account-balances/{sub_account}"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            df = json_normalize(result)
            return df
        else:
            print("Error:", response.text)

    def email_otp(self):
        """
        Trigger an email OTP request to DNSE. The OTP will be sent to the email address associated with the DNSE account.

        Returns:
            None.
        """
        url = "https://services.entrade.com.vn/dnse-auth-service/api/email-otp"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("OTP sent to email")
        else:
            print("Error:", response.text)
            return None

    def trading_token(self, otp):
        """
        Authenticate using OTP and get the trading token.

        Args:
            otp (str): OTP code for authentication.

        Returns:
            str: Trading token if authentication is successful, None otherwise.
        """
        url = "https://services.entrade.com.vn/dnse-order-service/trading-token"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "otp": otp
        }
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            trading_token = result.get("tradingToken")
            print("Authenticated! Trading token returned.")
            self.trading_token = trading_token
            return trading_token
        else:
            print("Error authenticating:", response.text)
            return None
        
    def loan_packages(self, sub_account, asset_type='stock'):
        """
        Get the list of loan packages for a specific sub account.

        Args:
            sub_account (str): DNSE sub account number (mã tiểu khoản).
            asset_type (str): Asset type, either 'stock' or 'derivative'.

        Returns:
            DataFrame: A DataFrame containing the list of loan packages if successful, None otherwise.
        """
        if asset_type == 'stock':
            url = f"https://services.entrade.com.vn/dnse-order-service/accounts/{sub_account}/loan-packages"
        elif asset_type == 'derivative':
            url = f"https://services.entrade.com.vn/dnse-order-service/accounts/{sub_account}/derivative-loan-packages"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            df = json_normalize(result['loanPackages'])
            return df
        else:
            print("Error:", response.text)
            return None
        
    def trade_capacities(self, symbol, price, sub_account, asset_type='stock', loan_package_id=None):
        """
        Get the list of trade capacities (sức mua/bán) for a specific sub account.

        Args:
            symbol (str): Symbol of the asset.
            price (float): Price of the asset, unit is VND.
            sub_account (str): DNSE sub account number (mã tiểu khoản).
            asset_type (str): Asset type, either 'stock' or 'derivative'.
            loan_package_id (int): Loan package ID (if applicable).
        Returns:
            DataFrame: A DataFrame containing the list of trade capacities if successful, None otherwise.
        """
        if asset_type == 'stock':
            url = f'https://services.entrade.com.vn/dnse-order-service/accounts/{sub_account}/ppse'
        elif asset_type == 'derivative':
            url = f'https://services.entrade.com.vn/dnse-order-service/accounts/{sub_account}/derivative-ppse?symbol={symbol}&price={price}&loanPackageId={loan_package_id}'
        # Add query param to the URL, if applicable (not None) ?symbol={symbol}&price={price}&loanPackageId={loan_package_id}
        query_params = {
            "symbol": symbol,
            "price": price,
            "loanPackageId": loan_package_id
        }
        
        # Filter out None values from query parameters
        query_params = {k: v for k, v in query_params.items() if v is not None}

        if query_params:
            url += "?" + "&".join([f"{key}={value}" for key, value in query_params.items()])

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            df = json_normalize(result)
            return df
        else:
            print("Error:", response.text)
            return None

    def place_order(self, sub_account, symbol, side, quantity, price, order_type, loan_package_id, asset_type='stock'):
        """
        Place an order for stocks or derivatives.

        Args:
            sub_account (str): Sub account number.
            symbol (str): Symbol of the asset.
            side (str): 'buy' or 'sell'.
            quantity (int): Order quantity.
            price (float): Order price.
            loan_package_id (int): Loan package ID (if applicable).
            asset_type (str): Asset type, either 'stock' or 'derivative'.

        Returns:
            DataFrame: A DataFrame containing the order information if successful, None otherwise.
        """
        if side == 'buy':
            side_code = 'NB'
        elif side == 'sell':
            side_code = 'NS'

        if asset_type == 'stock':
            url = "https://services.entrade.com.vn/dnse-order-service/v2/orders"
        elif asset_type == 'derivative':
            url = "https://services.entrade.com.vn/dnse-order-service/derivative/orders"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Trading-Token": self.trading_token
        }
        payload = {
            "accountNo": sub_account,
            "symbol": symbol,
            "side": side_code,
            "quantity": quantity,
            "price": price,
            'orderType': order_type,
            "loanPackageId": loan_package_id
        }
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        df = json_normalize(result)
        return df

    def order_list(self, sub_account, asset_type='stock'):
        """
        Get the list of orders for a specific account.

        Args:
            sub_account (str): DNSE sub account number (mã tiểu khoản).
            asset_type (str): Asset type, either 'stock' or 'derivative'.

        Returns:
            DataFrame: A DataFrame containing the list of orders if successful, None otherwise.
        """
        if asset_type == 'stock':
            url = f"https://services.entrade.com.vn/dnse-order-service/v2/orders?accountNo={sub_account}"
        elif asset_type == 'derivative':
            url = f"https://services.entrade.com.vn/dnse-order-service/derivative/orders?accountNo={sub_account}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print('Order list retrieved')
            df = json_normalize(result['orders'])
            return df
        else:
            print("Error:", response.text)
            return None
        
    def order_detail(self, order_id, sub_account, asset_type='stock'):
        """
        Get the details of a specific order for a specific sub account.
        Args:
            order_id (str): Order ID.
            sub_account (str): DNSE sub account number (mã tiểu khoản).
            asset_type (str): Asset type, either 'stock' or 'derivative'.
        """
        if asset_type == 'stock':
            url = f"https://services.entrade.com.vn/dnse-order-service/v2/orders/{order_id}?accountNo={sub_account}"
        elif asset_type == 'derivative':
            url = f"https://services.entrade.com.vn/dnse-order-service/derivative/orders/{order_id}?accountNo={sub_account}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            df = json_normalize(result)
            return df
        else:
            print("Error:", response.text)
            return None
    
    def cancel_order (self, order_id, sub_account, asset_type='stock'):
        """
        Cancel an order.
        Args:
            order_id (str): Order ID.
            sub_account (str): DNSE sub account number (mã tiểu khoản).
            asset_type (str): Asset type, either 'stock' or 'derivative'.
        """
        if asset_type == 'stock':
            url = f"https://services.entrade.com.vn/dnse-order-service/v2/orders/{order_id}?accountNo={sub_account}"
        elif asset_type == 'derivative':
            url = f"https://services.entrade.com.vn/dnse-order-service/derivative/orders/{order_id}?accountNo={sub_account}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print("Order cancelled")
            df = json_normalize(response.json())
            return df
        else:
            print("Error:", response.text)
            return None
        
    def deals_list (self, sub_account, asset_type='stock'):
        """
        Get the list of deals for a specific sub account.
        Args:
            sub_account (str): DNSE sub account number (mã tiểu khoản).
        """
        if asset_type == 'stock':
            url = f'https://services.entrade.com.vn/dnse-deal-service/deals?accountNo={sub_account}'
        elif asset_type == 'derivative':
            url = f'https://services.entrade.com.vn/dnse-derivative-core/deals?accountNo={sub_account}'

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print('Deals list retrieved')
            df = json_normalize(result['data'])
            return df
        else:
            print("Error:", response.text)
            return None

# SSI FAST CONNECT DATA
## Data Streaming
