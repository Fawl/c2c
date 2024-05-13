import csv
import datetime

from typing import Dict, List
from collections import deque, defaultdict
from queue import Queue


# from client import Client
# from instrument import Instrument


class Order:
    def __init__(self, time: datetime.datetime.Date, client, instrument, side: bool, price: float | None, quantity: int) -> None:
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
        self.time: datetime.datetime.date | None = time
        self.client: None = client # replace with client
        self.instrument: None = instrument # replace with instrument
        self.side: bool = side # TRUE: buy, FALSE: sell
        self.price: float | None = price # none: market, else price
        self.quantity: int | None = quantity

        # Result
        self.result: bool = None # success
        self.message: str = "Accept"

    def __str__(self):
        return f"{self.instrument} {self.side} {self.quantity} @ {self.price}"

    @property
    def side(self) -> bool:
        return self.side
    
    @property
    def price(self) -> float:
        return self.price
    
    @property
    def quantity(self) -> int:
        return self.quantity
    
    @property
    def client(self):
        return self.client
    
    @property
    def instrument(self):
        return self.instrument
    
    @property
    def time(self):
        return self.time


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
        self.trades = Queue()

    @property
    def max_bid(self) -> float:
        if self.bids:
            return max(self.bids.keys())
        else:
            return 0.0
        
    @property
    def min_offer(self) -> float:
        if self.offers:
            return min(self.offers.keys())
        else:
            return float('inf') 
        
    def get_new_order_id(self) -> int:
        self.order_id += 1
        return self.order_id
    
    def execute(self, buyer, seller, price: float, size: int) -> str:
        return f"{datetime.datetime.now()} EXECUTE: {buyer} BUY {seller} SELL {size} {self.__instrument} @ {price}"
        
    def process_order(self, incoming_order: Order) -> None:
        '''
        Attempt to fill an incoming order, if not add to OB
        '''
        new_ts = incoming_order.time
        new_order_id = self.get_new_order_id()

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
                incoming_qty: int = min(0, incoming_order.quantity) # guaranteed > 0 ?
                book_qty: int = min(0, book_order.quantity)

                trade_size: int = min(incoming_qty, book_qty)

                res: str = self.execute(incoming_order.client, book_order.client, price, trade_size)

                self.trades.put(res)

            levels[price] = [o for o in order_stack if o.quantity > 0]

            if len(levels[price] == 0): # no more orders at price
                levels.pop(price)

        if incoming_order.quantity > 0:
            orders_at_side = self.offers if is_sell else self.bids
            orders_at_side[incoming_order.price].append(incoming_order)

