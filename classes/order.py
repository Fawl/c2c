import csv
import datetime
import os
import heapq, logging
import copy

from typing import Dict, List, Tuple
from collections import defaultdict
from queue import Queue

from .instrument import Instrument



# from client import Client
# from instrument import Instrument
class Trade:
    def __init__(self, buyer, seller, price: float, volume: int) -> None:
        self.buyer = buyer
        self.seller = seller
        self.time = datetime.datetime.now()
        self.price = price
        self.volume = volume

    def __str__(self) -> str:
        return f"{self.time} BUY {self.buyer.ID} SELL {self.seller.ID} {self.volume} @ {self.price}"

class Order:
    def __init__(self, id: str, time: datetime.datetime.date, client, instrument, side: bool, price: float | None, quantity: float, rating: int) -> None:
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
        self.client = client # replace with client
        self.instrument = instrument # replace with instrument
        self.side: bool = side # TRUE: buy, FALSE: sell
        self.rating: int = rating

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
    
    def __lt__(self, obj):
        """self < obj."""
        if self.price == obj.price:
            if self.rating == obj.rating:
                return self.time > obj.time
            else:
                return self.rating > obj.rating
        else:
            if self.side: # buy
                return self.price < obj.price
            else: # sell
                return self.price > obj.price

    def __gt__(self, obj):
        """self > obj."""
        if self.price == obj.price:
            if self.rating == obj.rating:
                return self.time < obj.time
            else:
                return self.rating < obj.rating
        else:
            if self.side: # buy
                return self.price > obj.price
            else: # sell
                return self.price < obj.price


class OrderBook:
    def __init__(self, instrument, start_id: int = 0, callback = None) -> None:
        self.instrument: None = instrument
        self.order_id = start_id
        self.callback = callback

        self.bids: Dict[int, list] = defaultdict(list)
        self.offers: Dict[int, list] = defaultdict(list)

        self.trades = []
        self.log = []
        self.errors = []

        self.pre_orders = []
        self.post_orders = []

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
            return None
        
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
            return None
        
    def calculate_auction_price(self, auction_orders: List[Order]) -> float | None:
        bids = defaultdict(list)
        offers = defaultdict(list)

        for order in auction_orders:
            # print(order)
            rating = order.rating

            if order.side: # BUY
                bids[order.price].append(
                    (rating, order)
                )
                heapq.heapify(bids[order.price])
            else: # SELL
                offers[order.price].append(
                    (rating, order)
                )
                heapq.heapify(offers[order.price])

        # get max offer
        # get min bid

        max_offer = 0.0
        min_bid = 100000000.0

        for bid in bids:
            if bid is not None and min_bid > bid:
                min_bid = bid

        for offer in offers:
            if offer is not None and max_offer < offer:
                max_offer = offer

        # print(min_bid)
        # print(max_offer)

        market_bid = bids[None]
        bids.pop(None)
        bids[max_offer] = market_bid

        market_offer = offers[None]
        offers.pop(None)
        offers[min_bid] = market_offer

        bid_prices = sorted(bids.keys(), reverse=True)
        offer_prices = sorted(offers.keys())

        # print(offer_prices)

        bid_sizes = [sum(o[1].quantity for o in bids[p]) for p in bid_prices]
        offer_sizes = [sum(o[1].quantity for o in offers[p]) for p in offer_prices]

        # for bid 

        # # print(bid_prices)
        # # print(bid_sizes)

        # print(offer_prices)
        # print(offer_sizes)

        bid_to_qty = dict(zip(bid_prices, bid_sizes))
        bid_with_most = max(bid_to_qty, key = lambda x: bid_to_qty[x])
        bid_most_qty = bid_to_qty[bid_with_most]

        offer_to_qty = dict(zip(offer_prices, offer_sizes))
        sorted_offer_to_qty = {key : offer_to_qty[key] for key in sorted(offer_to_qty.keys())}

        for price, qty in sorted_offer_to_qty.items():
            bid_most_qty -= qty

            if bid_most_qty <= 0:
                return price

        
    def get_new_order_id(self) -> int:
        self.order_id += 1
        return self.order_id
    
    
    def generate_trade_log(self, incoming_order: Order, book_order, price: float, size: int) -> str:
        return f"{datetime.datetime.now()} EXECUTE: {incoming_order.client} #{incoming_order.id} BUY {book_order.client} #{book_order.id} SELL {size} {self.instrument} @ {price}"
        
    def process_order(self, incoming_order: Order, rating: int) -> None:
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

        order_client = incoming_order.client

        try:
            order_client.checkOrder(incoming_order)

            # before start
            if incoming_order.time <= datetime.datetime.strptime("09:30:00", "%H:%M:%S"):
                # print(incoming_order.time)
                # print(incoming_order)
                self.pre_orders.append(copy.deepcopy(incoming_order))
            # after end
            elif incoming_order.time >= datetime.datetime.strptime("16:00:00", "%H:%M:%S"):
                # print(incoming_order.time)
                self.post_orders.append(copy.deepcopy(incoming_order))

            if incoming_order.side: # BUY
                if incoming_order.price >= self.min_offer and self.offers:
                    self.process_match(incoming_order, rating)
                else:
                    self.bids[incoming_order.price].append(
                        (rating, incoming_order)
                    )
                    heapq.heapify(self.bids[incoming_order.price])
            else: # SELL
                incoming_order.client.updatePosition(incoming_order.instrument, incoming_order.price, -incoming_order.quantity)

                if incoming_order.price <= self.max_bid and self.bids:
                    self.process_match(incoming_order, rating)
                else:
                    self.offers[incoming_order.price].append(
                        (rating, incoming_order)
                    )
                    heapq.heapify(self.offers[incoming_order.price])

        except Exception as e:
            self.errors.append(f"{incoming_order.id}|{incoming_order.time}|{e}")

    def process_match(self, incoming_order: Order, rating: int, store_trade: bool = True) -> None:
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

            # order_pq: List[Tuple[int, Order]] = levels[price]

            for order_idx, book_order_with_rating in enumerate(levels[price]):
                rating, book_order = book_order_with_rating

                incoming_qty: int = max(0, incoming_order.quantity) # guaranteed > 0 ?
                book_qty: int = max(0, book_order.quantity)

                trade_size: int = min(incoming_qty, book_qty)

                # print(f"INC: {incoming_qty} BOOK: {book_qty} SIZE {trade_size}")

                incoming_order.quantity -= trade_size
                book_order.quantity -= trade_size

                if trade_size == 0:
                    continue

                Instrument.add_matching(incoming_order.instrument, incoming_order.price, trade_size)

                if store_trade:
                    self.trades.append(
                        Trade(
                            incoming_order.client,
                            book_order.client,
                            book_order.price,
                            trade_size
                        )
                    )

                    res: str = self.generate_trade_log(incoming_order, book_order, price, trade_size)
                    self.log.append(res)

                    # if not is_sell:
                    #     incoming_order.client.updatePosition(incoming_order.instrument, incoming_order.price, -trade_size)

                    if incoming_order.side:
                        incoming_order.client.updatePosition(incoming_order.instrument, incoming_order.price, trade_size)

                    if book_order.side:
                        book_order.client.updatePosition(book_order.instrument, book_order.price, trade_size)


            # Remove orders with quantity 0
            levels[price] = [o for o in levels[price] if o[1].quantity > 0]

            # for order_w_rating in levels[price]:
            #     rating, order = order_w_rating
            #     print(rating, order.quantity)

            heapq.heapify(levels[price])

            if len(levels[price]) == 0: # no more orders at price
                levels.pop(price)

        if incoming_order.quantity > 0:
            orders_at_side = self.offers if is_sell else self.bids
            orders_at_side[incoming_order.price].append((rating, incoming_order))

    def show_book(self):
        bid_prices = sorted(self.bids.keys(), reverse=True)
        offer_prices = sorted(self.offers.keys())

        bid_sizes = [sum(o[1].quantity for o in self.bids[p]) for p in bid_prices]
        offer_sizes = [sum(o[1].quantity for o in self.offers[p]) for p in offer_prices]

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
        if len(self.log) == 0:
            print("NO TRADES")
        else:
            for log in self.log:
                print(log)

            for error in self.errors:
                print(error)

            # for trade in self.trades:
            #     print(trade)

outputReportPath = os.path.join('reports', 'output_exchange_report.csv')

def generateExchangeReport(exchanges:list[OrderBook]):
    with open(outputReportPath, 'w') as report:
        
        fieldnames = ['OrderID', 'RejectionReason']
        writer = csv.DictWriter(report, fieldnames=fieldnames)
        writer.writeheader()

        for exchange in exchanges:
            try: 
                rows = []
                for error in exchange.errors:
                    stuffs = error.split('|')
                    if 'REJECTED' in stuffs[2]:
                        rows.append({
                            'OrderID' : stuffs[0],
                            'RejectionReason' : stuffs[2]
                        })
                writer.writerows(rows)
            except Exception as e:
                logging.error(f"Error occured when writing: {e}")

    logging.info('Completed report.')
    return