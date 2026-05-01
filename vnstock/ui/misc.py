class Misc:
    """
    Miscellaneous market tools.
    """

    def __init__(self):
        from vnstock.ui.domains.misc.tools import Misc as MiscDomain

        self._misc = MiscDomain()

    def exchange_rate(self, date: str = ""):
        return self._misc.exchange_rate(date=date)

    def gold_price_sjc(self, date: str = None):
        return self._misc.gold_price_sjc(date=date)

    def gold_price_btmc(self):
        return self._misc.gold_price_btmc()
