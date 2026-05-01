class Broker:
    """
    Brokerage Connectors.
    """

    @property
    def dnse(self):
        from vnstock.ui.domains.broker.dnse import DNSEBroker

        return DNSEBroker()
