import csv
import datetime
import os

from typing import Dict, List
from collections import defaultdict
from queue import Queue


# from client import Client
# from instrument import Instrument


class Order:
    def __init__(self, id: str, time: datetime.datetime.date, client, instrument, side: bool, price: float | None, quantity: int) -> None:
        '''
        Class representing a single order
        @param time: datetime
        @param client: Client object
        @param instrument: Instrument object
        @param side: boolean, TRUE=buy, FALSE=sell
        @param price: optional integer, none=market price
        @param quantity: int
        '''
        # From orderbook
        self.id = id
        self.time: datetime.datetime.date | None = time
        self.client: None = client # replace with client
        self.instrument: None = instrument # replace with instrument
        self.side: bool = side # TRUE: buy, FALSE: sell

        if price == "Market":
            self.price = None
        else:
            self.price = float(price)

        self.quantity: int | None = quantity

        # Result
        self.result: bool = None # success
        self.message: str = "Accept"

    def __str__(self):
        return f"{self.id} {self.instrument} {self.side} {self.quantity} @ {self.price}"


class OrderBook:
    def __init__(self, instrument, start_id: int = 0, callback = None) -> None:
        self.instrument: None = instrument
        self.order_id = start_id
        self.callback = callback

        self.bid_prices: List[float] = []
        self.bid_sizes: List[int] = []

        self.offer_prices: List[float] = []
        self.offer_sizes: List[int] = []

        self.bids: Dict[int, list] = defaultdict(list)
        self.offers: Dict[int, list] = defaultdict(list)

        self.to_process = Queue()
        self.trades = []

    @property
    def max_bid(self) -> float: # max amount people are willing to pay
        if self.bids:
            return max(self.bids.keys())
        else:
            return 0.0
        
    @property
    def min_bid(self) -> float:
        if self.bids:
            return min(self.bids.keys())
        else:
            return float('inf')
        
    @property
    def min_offer(self) -> float: # min amount people are willing to sell
        if self.offers:
            return min(self.offers.keys())
        else:
            return float('inf') 
        
    @property
    def max_offer(self) -> float:
        if self.offers:
            return max(self.offers.keys())
        else:
            return 0.0
        
        
    def get_new_order_id(self) -> int:
        self.order_id += 1
        return self.order_id
    
    def log(self, incoming_order, book_order, price: float, size: int) -> str:
        return f"{datetime.datetime.now()} EXECUTE: {incoming_order.client} #{incoming_order.id} BUY {book_order.client} #{book_order.id} SELL {size} {self.instrument} @ {price}"
        
    def process_order(self, incoming_order: Order) -> None:
        '''
        Attempt to fill an incoming order, if not add to OB
        '''
        new_ts = incoming_order.time
        new_order_id = self.get_new_order_id()

        if incoming_order.price is None: # Market order
            if incoming_order.side: # BUY at highest sell price
                incoming_order.price = self.max_offer
            else: # SELL at lowest buy price
                incoming_order.price = self.min_bid

        # TODO: Add checks (?)

        if incoming_order.side: # BUY
            if incoming_order.price >= self.min_offer and self.offers:
                self.process_match(incoming_order)
            else:
                self.bids[incoming_order.price].append(incoming_order)
        else: # SELL
            if incoming_order.price <= self.max_bid and self.bids:
                self.process_match(incoming_order)
            else:
                self.offers[incoming_order.price].append(incoming_order)

    def process_match(self, incoming_order: Order) -> None:
        '''
        Matching algo, price-time (add rating later) priority
        '''
        is_sell: bool = not incoming_order.side

        levels: List[float] = self.bids if is_sell else self.offers
        prices: List[float] = sorted(levels.keys(), reverse=is_sell)

        def does_not_match(book_price: float) -> bool:
            if is_sell:
                return incoming_order.price > book_price
            else:
                return incoming_order.price < book_price
            
        for price_idx, price in enumerate(prices):
            # Check here?
            if incoming_order.quantity == 0 or does_not_match(price):
                break

            order_stack: List[Order] = levels[price]

            for order_idx, book_order in enumerate(order_stack):
                incoming_qty: int = max(0, incoming_order.quantity) # guaranteed > 0 ?
                book_qty: int = max(0, book_order.quantity)

                trade_size: int = min(incoming_qty, book_qty)

                # print(f"INC: {incoming_qty} BOOK: {book_qty} SIZE {trade_size}")

                incoming_order.quantity -= trade_size
                book_order.quantity -= trade_size

                res: str = self.log(incoming_order, book_order, price, trade_size)

                self.trades.append(res)

            levels[price] = [o for o in order_stack if o.quantity > 0]

            if len(levels[price]) == 0: # no more orders at price
                levels.pop(price)

        if incoming_order.quantity > 0:
            orders_at_side = self.offers if is_sell else self.bids
            orders_at_side[incoming_order.price].append(incoming_order)

    def show_book(self):
        bid_prices = sorted(self.bids.keys(), reverse=True)
        offer_prices = sorted(self.offers.keys())

        bid_sizes = [sum(o.quantity for o in self.bids[p]) for p in bid_prices]
        offer_sizes = [sum(o.quantity for o in self.offers[p]) for p in offer_prices]

        print()
        print("=== BOOK ===")

        print('SELL')
        if len(offer_prices) == 0:
            print('NO SELLS')
        for idx, price in reversed(list(enumerate(offer_prices))):
            print(f"{idx + 1} {price} {offer_sizes[idx]}")

        print('BUY')
        if len(bid_prices) == 0:
            print('NO BUYS')
        for idx, price in list(enumerate(bid_prices)):
            print(f"{idx + 1} {price} {bid_sizes[idx]}")

        print()

        print("=== TRADES ===")
        if len(self.trades) == 0:
            print("NO TRADES")
        else:
            for trade in self.trades:
                print(trade)

    