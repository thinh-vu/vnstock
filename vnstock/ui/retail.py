from vnai import optimize_execution

class Retail:
    """
    Retail Data Layer for vnstock (Gold, Exchange Rates).
    """
    def __init__(self):
        from vnstock.ui.domains.retail.commodity import Retail as RetailDomain
        self._retail = RetailDomain()

    @optimize_execution("UI")
    def gold(self, source: str = 'sjc', date: str = None):
        """Access gold price data."""
        return self._retail.gold(source=source, date=date)

    @optimize_execution("UI")
    def exchange_rate(self, date: str = ''):
        """Access exchange rate data."""
        return self._retail.exchange_rate(date=date)
