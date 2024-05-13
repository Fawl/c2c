import csv

class Instrument:

    def __init__(self, instrumentID, currency, lotSize) -> None:
        self.instrumentID = instrumentID
        self.currency = currency
        self.lotSize = lotSize
        self.open_price = None
        self.closed_price = None
        self.total_traded_volume = 0
        self.day_high = None
        self.day_low = None
        self.matchings = []

    def get_instrument_currency(self):
        return self.currency

    def get_lotSize(self):
        return self.lotSize

    def add_matching(self, price, volume):
        self.matchings.append((price, volume))
        self.total_traded_volume += volume
        if self.open_price is None:
            self.open_price = price
        self.day_high = max(self.day_high, price) if self.day_high is not None else price
        self.day_low = min(self.day_low, price) if self.day_low is not None else price


