from typing import Optional, Any, Dict
import pandas as pd
from vnstock.ui._base import BaseUI

class DNSEBroker(BaseUI):
    """DNSE Brokerage integration."""
    
    def login(self, user_name: str, password: str) -> Optional[str]:
        """Authenticate with DNSE."""
        return self._dispatch('dnse', 'login', user_name=user_name, password=password)

    def account(self) -> Optional[pd.DataFrame]:
        """Get user profile info."""
        return self._dispatch('dnse', 'account')

    def sub_accounts(self) -> Optional[pd.DataFrame]:
        """List all sub-accounts."""
        return self._dispatch('dnse', 'sub_accounts')

    def account_balance(self, sub_account: str) -> Optional[pd.DataFrame]:
        """Get balance for a specific sub-account."""
        return self._dispatch('dnse', 'account_balance', sub_account=sub_account)

    def email_otp(self) -> None:
        """Trigger email OTP."""
        return self._dispatch('dnse', 'email_otp')

    def get_trading_token(self, otp: str, smart_otp: bool = True) -> Optional[str]:
        """Get trading token using OTP."""
        return self._dispatch('dnse', 'get_trading_token', otp=otp, smart_otp=smart_otp)

    def loan_packages(self, sub_account: str, asset_type: str = 'stock') -> Optional[pd.DataFrame]:
        """List available loan packages."""
        return self._dispatch('dnse', 'loan_packages', sub_account=sub_account, asset_type=asset_type)

    def trade_capacities(self, symbol: str, price: float, sub_account: str, asset_type: str = 'stock', loan_package_id: Optional[int] = None) -> Optional[pd.DataFrame]:
        """Get buying/selling power."""
        return self._dispatch('dnse', 'trade_capacities', symbol=symbol, price=price, sub_account=sub_account, asset_type=asset_type, loan_package_id=loan_package_id)

    def place_order(self, sub_account: str, symbol: str, side: str, quantity: int, price: float, order_type: str, loan_package_id: Optional[int], asset_type: str = 'stock') -> Optional[pd.DataFrame]:
        """Place a new order."""
        return self._dispatch('dnse', 'place_order', sub_account=sub_account, symbol=symbol, side=side, quantity=quantity, price=price, order_type=order_type, loan_package_id=loan_package_id, asset_type=asset_type)

    def order_list(self, sub_account: str, asset_type: str = 'stock') -> Optional[pd.DataFrame]:
        """List all orders."""
        return self._dispatch('dnse', 'order_list', sub_account=sub_account, asset_type=asset_type)

    def order_detail(self, order_id: str, sub_account: str, asset_type: str = 'stock') -> Optional[pd.DataFrame]:
        """Get details of a specific order."""
        return self._dispatch('dnse', 'order_detail', order_id=order_id, sub_account=sub_account, asset_type=asset_type)

    def cancel_order(self, order_id: str, sub_account: str, asset_type: str = 'stock') -> Optional[pd.DataFrame]:
        """Cancel an existing order."""
        return self._dispatch('dnse', 'cancel_order', order_id=order_id, sub_account=sub_account, asset_type=asset_type)

    def deals_list(self, sub_account: str, asset_type: str = 'stock') -> Optional[pd.DataFrame]:
        """List all deals."""
        return self._dispatch('dnse', 'deals_list', sub_account=sub_account, asset_type=asset_type)

class Broker(BaseUI):
    """Brokerage Connectors."""
    @property
    def dnse(self) -> DNSEBroker:
        return DNSEBroker()
