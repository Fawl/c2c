import csv

class Instrument:

    INSTRUMENTS = set()

    def __init__(self, instrumentID: str, currency: str, lotSize: int) -> None:
        self.instrumentID = instrumentID
        self.currency = currency
        self.lotSize = lotSize
        self.open_price : float = None
        self.closed_price : float = None
        self.total_traded_volume : int = 0
        self.day_high : float = None
        self.day_low : float = None
        self.matchings : list = []
        Instrument.INSTRUMENTS.add(instrumentID)

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
        

        total_price_volume = sum([price * volume for price, volume in self.matchings])
        vwap = round(total_price_volume / self.total_traded_volume, 4) if self.total_traded_volume != 0 else 0

        instrumentRows = [{
            'Instrument ID': self.instrumentID,
            'OpenPrice': self.open_price,
            'ClosePrice': self.closed_price,
            'TotalVolume': self.total_traded_volume,
            'VWAP': vwap,
            'DayHigh': self.day_high,
            'DayLow': self.day_low
        }]

        filename = "output_instrument_report.csv"

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)

            writer.writeheader()

            writer.writerows(instrumentRows)
