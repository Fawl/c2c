import csv
import order
import instrument

data = csv.DictReader(open(r'classes/csv/example/input_clients.csv'))

class client:

    def __init__(self, ID: str, currencies: set, positionCheck: bool, rating: int) -> None:
        self.ID = ID
        self.currencies = currencies

        # if true, no shorts
        self.positionCheck = positionCheck

        # 1 to 10
        self.rating = rating
        """
        {
            instrumentID : {
                price : qty
            }
        }
        """
        self.positions: dict[instrument:dict[float:int]] = {}

    def updatePosition(self, order: order) -> dict[float:int]:
        
        if order.instrument in self.positions:
            self.positions[order.instrument][order.price] = order.qty + self.positions[order.instrument].setdefault(order.price, 0)

        else:
            self.positions[order.instrument] = {order.price : order.qty}
        
        return self.positions[order.instrument]
    

    def generateReport(self) -> list[dict[str:str|int]]:
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
            clientRows.push({
                'InstrumentID' : instrument,
                'NetPosition' : sum(fulfilled.values())
            })
        
        return clientRows








