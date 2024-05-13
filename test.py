from classes.client import Client, generateClientReport
from classes.order import Order, OrderBook, generateExchangeReport
from classes.instrument import Instrument, generate_instrument_report

from typing import List

import os
import csv
import datetime

def main() -> None:
    inputClientPath = os.path.join('classes', 'csv', 'test', 'input_clients.csv')
    inputInstrumentPath = os.path.join('classes', 'csv', 'test', 'input_instruments.csv')
    inputOrderPath = os.path.join('classes', 'csv', 'test', 'input_orders.csv')
    clientData = csv.DictReader(open(inputClientPath))
    instrumentData = csv.DictReader(open(inputInstrumentPath))
    clients = {}
    instruments = {}
    orderbooks = {}

    # INSTRUMENT INGESTION
    for instrument in instrumentData:
        instruments[instrument['InstrumentID']] = Instrument(instrument['InstrumentID'], instrument['Currency'], int(instrument['LotSize']))
        orderbooks[instrument['InstrumentID']] = OrderBook(instrument['InstrumentID'])

    # CLIENT INGESTION
    for row in clientData:
        newclient = Client(
                    ID= row['ClientID'],
                    currencies= set(row['Currencies'].split(',')),
                    positionCheck= True if row['PositionCheck'] == 'Y' else False,
                    rating= int(row['Rating'])
                )
        clients[row['ClientID']] = newclient

    # FOR TESTING 
    # pre_orders = [
    #     Order("C1", datetime.datetime.now(), clients['C'], instruments['SIA'], True, 32.0, 100, clients['C'].rating),
    #     Order("A2", datetime.datetime.now(), clients['A'], instruments['SIA'], True, 31.9, 800, clients['A'].rating),
    #     Order("B1", datetime.datetime.now(), clients['B'], instruments['SIA'], False, 32.1, 4000, clients['B'].rating)
    # ]

    orders: List[Order] = []

    sia_inst = Instrument("SIA", "SGD", 100)

    # pre_orders = [
    #     Order("C1", datetime.datetime.now(), clients['C'], sia_inst, True, 32.0, 100, clients['C'].rating),
    #     Order("A2", datetime.datetime.now(), clients['A'], sia_inst, True, 31.9, 800, clients['A'].rating),
    #     Order("B1", datetime.datetime.now(), clients['B'], sia_inst, False, 32.1, 4000, clients['B'].rating)
    # ]

    # for order in pre_orders:
    #     ob.process_order(order, order.rating)

    # print(pre_orders)

    # ORDER INGESTION

    with open(inputOrderPath) as inf:
        csv_file = csv.DictReader(inf)

        for line in csv_file:
            client: Client = clients[line['Client']]

            new_order = Order(
                id=line['OrderID'],
                time=datetime.datetime.strptime(line['Time'], "%H:%M:%S"), 
                client=client,
                instrument=instruments[line['Instrument']],
                side=line["Side"] == "Buy",
                price=line["Price"],
                quantity=float(line["Quantity"]),
                rating=client.rating
            )

            orders.append(new_order)

    # ORDER PROCESSING
    for order in orders:
        ob: OrderBook = orderbooks[order.instrument.instrumentID]
        ob.process_order(order, order.rating)

    open_price = ob.calculate_auction_price(ob.pre_orders)
    close_price = ob.calculate_auction_price(ob.post_orders)

    print(open_price)
    print(close_price)
        # ob.calculate_auction_price(ob.post_orders)

        # ob.show_book()
    generateClientReport(clients.values())
    generate_instrument_report(instruments.values())
    generateExchangeReport(orderbooks.values())


if __name__ == '__main__':
    main()