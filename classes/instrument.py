class Instrument:

    INSTRUMENTS = set()

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
        Instrument.INSTRUMENTS.add(instrumentID)

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

    def generate_report(self):
        """
        Generate instrument report
        """

        fields = ['Instrument ID', 'OpenPrice', 'ClosePrice', 'TotalVolume', 'VWAP', 'DayHigh', 'DayLow']

        instrumentRows = []

        total_price_volume = sum([price * volume for price, volume in self.matchings]) # need jareds matching
        vwap = round(total_price_volume / self.total_traded_volume, 4)

        instrumentRows.push({
            'Instrument ID': self.instrumentID,
            'OpenPrice': self.open_price,
            'ClosePrice': self.closed_price,
            'TotalVolume': self.total_traded_volume,
            'VWAP': vwap,
            'DayHigh': self.day_high,
            'DayLow': self.day_low
        })

        filename = "output_instrument_report.csv"

        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
    
            writer.writeheader(fields)

            writer.writerows(instrumentRows)
