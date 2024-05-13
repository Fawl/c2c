import os, logging, csv
from order import Order
from instrument import Instrument
from errors import *


inputClientPath = os.path.join('classes', 'csv', 'example', 'input_clients.csv')
outputClientPath = os.path.join('reports', 'output_client_report.csv')
data = csv.DictReader(open(inputClientPath))
global INSTRUMENTS
INSTRUMENTS = set('SIA', 'AMD')

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
        self.positions: dict[Instrument:dict[float:int]] = {}

    def checkOrder(self, order: Order):

        if order.Instrument not in INSTRUMENTS:
            raise InstrumentNotFound()

        if order.instrument.currency not in self.currencies:
            raise MismatchCurrency()

        if order.quantity % order.instrument.lotSize != 0:
            raise InvalidSize()

        if sum(self.positions[order.instrument].values()) < order.quantity:
            raise PositionCheck()

        return True


    def updatePosition(self, order: Order) -> dict[float:int]:
        """
        Updates a client's position based on order. Returns position held by client for that particular instrument.
        """

        if order.instrument in self.positions:
            self.positions[order.instrument][order.price] = order.qty + self.positions[order.instrument].setdefault(order.price, 0)

        else:
            self.positions[order.instrument] = {order.price : order.qty}
        
        return self.positions[order.instrument]


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



if __name__ == "__main__":

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

