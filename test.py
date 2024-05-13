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

    for id, client in clients.items():
        print(id, client)

    ob = OrderBook("SIA")
    orders: List[Order] = []

    sia_inst = Instrument("SIA", "SGD", 100)

    pre_orders = [
        Order("C1", "abcd", "C", "SIA", True, 32.0, 100),
        Order("A2", "abcd", "A", "SIA", True, 31.9, 800),
        Order("B1", "abcd", "B", "SIA", False, 32.1, 4000)
    ]

    for order in pre_orders:
        ob.process_order(order)

    # ob.show_book()

    with open("classes//csv//example//input_orders_test.csv") as inf:
        csv_file = csv.DictReader(inf)

        for line in csv_file:
            client: Client = clients[line['Client']]

            new_order = Order(
                id=line['OrderID'],
                time=datetime.datetime.now(), 
                client=line['Client'],
                instrument=sia_inst,
                side=line["Side"] == "Buy",
                price=line["Price"],
                quantity=int(line["Quantity"])
            )

            if client.checkOrder(new_order):
                orders.append(new_order)

        for order in orders:
            ob.process_order(order)

        ob.show_book()


if __name__ == '__main__':
    main()