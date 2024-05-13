import os, logging, csv
from .order import Order
from .instrument import Instrument
from .errors import *


inputClientPath = os.path.join('classes', 'csv', 'example', 'input_clients.csv')
outputClientPath = os.path.join('reports', 'output_client_report.csv')
data = csv.DictReader(open(inputClientPath))
global INSTRUMENTS
INSTRUMENTS = set(['SIA', 'AMD'])

class Client:

    def __init__(self, ID: str, currencies: set[str], positionCheck: bool, rating: int) -> None:
        '''
        Class representing a single client
        @param ID: str
        @param currencies: Set of strings
        @param positionCheck: boolean
        @param rating: int
        '''
        self.ID = ID
        self.currencies = currencies

        # if true, no shorts
        self.positionCheck = positionCheck

        # 1 to 10
        self.rating = rating
        """
        {
            instrumentID : {
                price : qty,
                ...
            },
            ...
        }
        """
        self.positions: dict[str:dict[float:int]] = {}


    def __str__(self):
        # return f"{self.ID}: Allowed: [{self.currencies}] PosCheck: {self.positionCheck} Rating {self.rating}"
        return self.ID

    def checkOrder(self, order: Order):

        if order.instrument.instrumentID not in Instrument.INSTRUMENTS:
            raise InstrumentNotFound("REJECTED - INSTRUMENT NOT FOUND")

        if order.instrument.currency not in self.currencies:
            raise MismatchCurrency("REJECTED - MISMATCH CURRENCY")

        if order.quantity % order.instrument.lotSize != 0:
            raise InvalidSize("REJECTED - INVALID LOT SIZE")

        if not order.side and order.instrument.instrumentID in self.positions and sum(self.positions[order.instrument.instrumentID].values()) < order.quantity:
            raise PositionCheck("REJECTED - POSITION CHECK FAILED")

        return True


    def updatePosition(self, instrument: Instrument, price: float, qty: int) -> dict[float:int]:
        """
        Updates a client's position based on order. Returns position held by client for that particular instrument.
        """

        if instrument.instrumentID in self.positions:
            self.positions[instrument.instrumentID][price] = qty + self.positions[instrument.instrumentID].setdefault(price, 0)

        else:
            self.positions[instrument.instrumentID] = {price : qty}
        
        return self.positions[instrument.instrumentID]


    def generateReportRows(self) -> list[dict[str:str|int]]:
        """
        Returns a list of objects with keys being the header of the client report

        example:
        [
            {
                'InstrumentID' : 'SIA',
                'NetPosition' : 123
            },
            {
                'InstrumentID' : 'AMD',
                'NetPosition' : -213
            },
            ...
        ]
        """

        clientRows = []
        for instrument, fulfilled in self.positions.items():
            clientRows.append({
                'ClientID' : self.ID,
                'InstrumentID' : instrument,
                'NetPosition' : sum(fulfilled.values())
            })
        
        return clientRows


def main():
    test = []
    for row in data:
        newclient = Client(
                    ID= row['ClientID'],
                    currencies= set(row['Currencies'].split(',')),
                    positionCheck= True if row['PositionCheck'] == 'Y' else False,
                    rating= int(row['Rating'])
                )
        test.append(newclient)

    for c in test:
        attrs = vars(c)
        # {'kids': 0, 'name': 'Dog', 'color': 'Spotted', 'age': 10, 'legs': 2, 'smell': 'Alot'}
        # now dump this in some way or another
        logging.debug(', '.join("%s: %s" % item for item in attrs.items()))

if __name__ == "__main__":
    main()


def generateClientReport(clients: list[Client]):

    with open(outputClientPath, 'w') as report:
        
        fieldnames = ['ClientID', 'InstrumentID', 'NetPosition']
        writer = csv.DictWriter(report, fieldnames=fieldnames)
        writer.writeheader()

        for c in clients:
            try: 
                logging.info(f"Writing for client {c.ID}...")
                writer.writerows(c.generateReportRows())
            except Exception as e:
                logging.error(f"Error occured when writing: {e}")

    logging.info('Completed report.')
    return