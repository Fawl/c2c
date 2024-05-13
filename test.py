from classes.client import Client
from classes.order import Order, OrderBook
from classes.instrument import Instrument

from typing import List

import os
import csv
import datetime

def main() -> None:
    inputClientPath = os.path.join('classes', 'csv', 'example', 'input_clients.csv')
    data = csv.DictReader(open(inputClientPath))
    clients = {}

    for row in data:
        newclient = Client(
                    ID= row['ClientID'],
                    currencies= set(row['Currencies'].split(',')),
                    positionCheck= True if row['PositionCheck'] == 'Y' else False,
                    rating= int(row['Rating'])
                )
        clients[row['ClientID']] = newclient

    # for id, client in clients.items():
    #     print(id, client)

    ob = OrderBook("SIA")
    orders: List[Order] = []

    sia_inst = Instrument("SIA", "SGD", 100)

    pre_orders = [
        Order("C1", datetime.datetime.now(), clients['C'], sia_inst, True, 32.0, 100, clients['C'].rating),
        Order("A2", datetime.datetime.now(), clients['A'], sia_inst, True, 31.9, 800, clients['A'].rating),
        Order("B1", datetime.datetime.now(), clients['B'], sia_inst, False, 32.1, 4000, clients['B'].rating)
    ]

    for order in pre_orders:
        ob.process_order(order, order.rating)

    # print(pre_orders)

    # ob.show_book()

    with open("classes//csv//example//input_orders.csv") as inf:
        csv_file = csv.DictReader(inf)

        for line in csv_file:
            client: Client = clients[line['Client']]

            new_order = Order(
                id=line['OrderID'],
                time=datetime.datetime.now(), 
                client=client,
                instrument=sia_inst,
                side=line["Side"] == "Buy",
                price=line["Price"],
                quantity=int(line["Quantity"]),
                rating=client.rating
            )

            # if client.checkOrder(new_order):
            orders.append(new_order)

        # print(orders)
        for order in orders:
            ob.process_order(order, order.rating)

        ob.show_book()


if __name__ == '__main__':
    main()