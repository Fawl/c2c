
class instrument:

    def __init__(self, instrumentID, currency, lotSize) -> None:
        self.instrumentID = instrumentID
        self.currency = currency
        self.lotSize = lotSize

    def get_instrument_currency(self):
        return self.currency

    def get_lotSize(self):
        return self.lotSize