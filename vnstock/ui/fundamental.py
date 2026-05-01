from vnai import optimize_execution


class Fundamental:
    """
    Fundamental Data Layer (Layer 3).
    """

    @optimize_execution("UI")
    def equity(self, symbol: str):
        """Access equity fundamental data."""
        from vnstock.ui.domains.fundamental.equity import EquityFundamental

        return EquityFundamental(symbol=symbol)
