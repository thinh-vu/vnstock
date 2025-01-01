import requests
import json
import pandas as pd
from pandas import json_normalize
from typing import Optional

class Trade:
    def __init__(self):
        self.token: Optional[str] = None
        self.trading_token: Optional[str] = None

    def login(self, user_name: str, password: str) -> Optional[str]:
        """
        Authenticate the user and obtain a JWT token for further API requests.

        Args:
            user_name (str): DNSE username. Can be 064CXXXXX, your email, or your phone number.
            password (str): Your DNSE password.

        Returns:
            Optional[str]: JWT token if authentication is successful, None otherwise.
        """
        url = "https://services.entrade.com.vn/dnse-user-service/api/auth"
        payload = json.dumps({'username': user_name, 'password': password})
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            print('Login successfully')
            self.token = response.json().get('token')
            return self.token
        else:
            print(f'Login failed: {response.text}')
            return None

    def account(self) -> Optional[pd.DataFrame]:
        """
        Get the full user profile from DNSE.

        Returns:
            Optional[pd.DataFrame]: A DataFrame containing the user profile if successful, None otherwise.
        """
        url = "https://services.entrade.com.vn/dnse-user-service/api/me"
        headers = {
            'Content-Type': 'text/plain',
            'Authorization': f'Bearer {self.token}'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print('Get profile successfully')
            return pd.DataFrame(response.json(), index=[0])
        else:
            print(f'Get profile failed: {response.text}')
            return None

    def sub_accounts(self) -> Optional[pd.DataFrame]:
        """
        Get sub-accounts information.

        Returns:
            Optional[pd.DataFrame]: A DataFrame containing the sub-accounts information if successful, None otherwise.
        """
        url = "https://services.entrade.com.vn/dnse-order-service/accounts"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return json_normalize(result.get('accounts', []))
        else:
            print(f"Error: {response.text}")
            return None

    def account_balance(self, sub_account: str) -> Optional[pd.DataFrame]:
        """
        Get account balance for a specific sub-account.

        Args:
            sub_account (str): DNSE sub account number (mã tiểu khoản).

        Returns:
            Optional[pd.DataFrame]: A DataFrame containing the account balance if successful, None otherwise.
        """
        url = f"https://services.entrade.com.vn/dnse-order-service/account-balances/{sub_account}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return json_normalize(result)
        else:
            print(f"Error: {response.text}")
            return None

    def email_otp(self) -> None:
        """
        Trigger an email OTP request to DNSE. The OTP will be sent to the email address associated with the DNSE account.
        """
        url = "https://services.entrade.com.vn/dnse-auth-service/api/email-otp"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("OTP sent to email")
        else:
            print(f"Error: {response.text}")

    def get_trading_token(self, otp: str, smart_otp: bool = True) -> Optional[str]:
        """
        Authenticate using OTP and get the trading token.

        Args:
            otp (str): OTP code for authentication. Input as a string.
            smart_otp (bool): Indicates if smart OTP is used. Default is True.

        Returns:
            Optional[str]: Trading token if authentication is successful, None otherwise.
        """
        url = "https://services.entrade.com.vn/dnse-order-service/trading-token" if smart_otp else "https://services.entrade.com.vn/dnse-auth-service/api/email-otp"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "smart-otp" if smart_otp else "otp": otp
        }
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            trading_token = response.json().get("tradingToken")
            print("Authenticated! Trading token returned.")
            self.trading_token = trading_token
            return trading_token
        else:
            print(f"Error authenticating: {response.text}")
            return None

    def loan_packages(self, sub_account: str, asset_type: str = 'stock') -> Optional[pd.DataFrame]:
        """
        Get the list of loan packages for a specific sub account.

        Args:
            sub_account (str): DNSE sub account number (mã tiểu khoản).
            asset_type (str): Asset type, either 'stock' or 'derivative'. Default is 'stock'.

        Returns:
            Optional[pd.DataFrame]: A DataFrame containing the list of loan packages if successful, None otherwise.
        """
        url = f"https://services.entrade.com.vn/dnse-order-service/accounts/{sub_account}/{'loan-packages' if asset_type == 'stock' else 'derivative-loan-packages'}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return json_normalize(result.get('loanPackages', []))
        else:
            print(f"Error: {response.text}")
            return None

    def trade_capacities(self, symbol: str, price: float, sub_account: str, asset_type: str = 'stock', loan_package_id: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        Get the list of trade capacities (sức mua/bán) for a specific sub account.

        Args:
            symbol (str): Symbol of the asset.
            price (float): Price of the asset, unit is VND.
            sub_account (str): DNSE sub account number (mã tiểu khoản).
            asset_type (str): Asset type, either 'stock' or 'derivative'. Default is 'stock'.
            loan_package_id (Optional[int]): Loan package ID (if applicable).

        Returns:
            Optional[pd.DataFrame]: A DataFrame containing the list of trade capacities if successful, None otherwise.
        """
        base_url = f'https://services.entrade.com.vn/dnse-order-service/accounts/{sub_account}/'
        endpoint = 'ppse' if asset_type == 'stock' else f'derivative-ppse?symbol={symbol}&price={price}&loanPackageId={loan_package_id}'
        url = base_url + endpoint

        query_params = {
            "symbol": symbol,
            "price": price,
            "loanPackageId": loan_package_id
        }
        query_params = {k: v for k, v in query_params.items() if v is not None}
        if query_params:
            url += "?" + "&".join([f"{key}={value}" for key, value in query_params.items()])

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return json_normalize(response.json())
        else:
            print(f"Error: {response.text}")
            return None

    def place_order(self, sub_account: str, symbol: str, side: str, quantity: int, price: float, order_type: str, loan_package_id: Optional[int], asset_type: str = 'stock') -> Optional[pd.DataFrame]:
        """
        Place an order for stocks or derivatives.

        Args:
            sub_account (str): Sub account number.
            symbol (str): Symbol of the asset.
            side (str): 'buy' or 'sell'.
            quantity (int): Order quantity.
            price (float): Order price.
            order_type (str): Order type.
            loan_package_id (Optional[int]): Loan package ID (if applicable).
            asset_type (str): Asset type, either 'stock' or 'derivative'. Default is 'stock'.

        Returns:
            Optional[pd.DataFrame]: A DataFrame containing the order information if successful, None otherwise.
        """
        side_code = 'NB' if side == 'buy' else 'NS'

        url = "https://services.entrade.com.vn/dnse-order-service/v2/orders" if asset_type == 'stock' else "https://services.entrade.com.vn/dnse-order-service/derivative/orders"
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
        if response.status_code == 200:
            return json_normalize(response.json())
        else:
            print(f"Error: {response.text}")
            return None

    def order_list(self, sub_account: str, asset_type: str = 'stock') -> Optional[pd.DataFrame]:
        """
        Get the list of orders for a specific account.

        Args:
            sub_account (str): DNSE sub account number (mã tiểu khoản).
            asset_type (str): Asset type, either 'stock' or 'derivative'. Default is 'stock'.

        Returns:
            Optional[pd.DataFrame]: A DataFrame containing the list of orders if successful, None otherwise.
        """
        url = f"https://services.entrade.com.vn/dnse-order-service/v2/orders?accountNo={sub_account}" if asset_type == 'stock' else f"https://services.entrade.com.vn/dnse-order-service/derivative/orders?accountNo={sub_account}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print('Order list retrieved')
            return json_normalize(response.json().get('orders', []))
        else:
            print(f"Error: {response.text}")
            return None

    def order_detail(self, order_id: str, sub_account: str, asset_type: str = 'stock') -> Optional[pd.DataFrame]:
        """
        Get the details of a specific order for a specific sub account.

        Args:
            order_id (str): Order ID.
            sub_account (str): DNSE sub account number (mã tiểu khoản).
            asset_type (str): Asset type, either 'stock' or 'derivative'. Default is 'stock'.

        Returns:
            Optional[pd.DataFrame]: A DataFrame containing the order details if successful, None otherwise.
        """
        url = f"https://services.entrade.com.vn/dnse-order-service/v2/orders/{order_id}?accountNo={sub_account}" if asset_type == 'stock' else f"https://services.entrade.com.vn/dnse-order-service/derivative/orders/{order_id}?accountNo={sub_account}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return json_normalize(response.json())
        else:
            print(f"Error: {response.text}")
            return None

    def cancel_order(self, order_id: str, sub_account: str, asset_type: str = 'stock') -> Optional[pd.DataFrame]:
        """
        Cancel an order.

        Args:
            order_id (str): Order ID.
            sub_account (str): DNSE sub account number (mã tiểu khoản).
            asset_type (str): Asset type, either 'stock' or 'derivative'. Default is 'stock'.

        Returns:
            Optional[pd.DataFrame]: A DataFrame containing the cancellation result if successful, None otherwise.
        """
        url = f"https://services.entrade.com.vn/dnse-order-service/v2/orders/{order_id}?accountNo={sub_account}" if asset_type == 'stock' else f"https://services.entrade.com.vn/dnse-order-service/derivative/orders/{order_id}?accountNo={sub_account}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print("Order cancelled")
            return json_normalize(response.json())
        else:
            print(f"Error: {response.text}")
            return None

    def deals_list(self, sub_account: str, asset_type: str = 'stock') -> Optional[pd.DataFrame]:
        """
        Get the list of deals for a specific sub account.

        Args:
            sub_account (str): DNSE sub account number (mã tiểu khoản).
            asset_type (str): Asset type, either 'stock' or 'derivative'. Default is 'stock'.

        Returns:
            Optional[pd.DataFrame]: A DataFrame containing the list of deals if successful, None otherwise.
        """
        url = f'https://services.entrade.com.vn/dnse-deal-service/deals?accountNo={sub_account}' if asset_type == 'stock' else f'https://services.entrade.com.vn/dnse-derivative-core/deals?accountNo={sub_account}'
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print('Deals list retrieved')
            return json_normalize(response.json().get('data', []))
        else:
            print(f"Error: {response.text}")
            return None
