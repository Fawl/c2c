import unittest
from client import Client
from order import Order, OrderBook
from instrument import Instrument
from errors import *

class Testing(unittest.TestCase):

    BOOK = OrderBook()
    i1 = Instrument('SIA', 'SGD', 100)
    o1 = Order(time='9:29:02', client='E1', instrument='SIA', quantity='12', price=32, side=False)
    c1 = Client('B', set(['USD', 'JPY']), False, 2)

    o2_INVALID_INSTRUMENT = Order(time='9:29:02', client='E1', instrument='AMD', quantity='1000', price=32, side=True)
    o2_INVALID_SIZE = Order(time='9:29:02', client='E1', instrument='SIA', quantity='12', price=32, side=True)

    def testNoInstrument(self):
        self.assertRaises(InstrumentNotFound, self.c1.checkOrder(self.o2_INVALID_INSTRUMENT))

    def testMismatchCurrency(self):
        self.assertRaises(MismatchCurrency, self.c1.checkOrder(self.o1))

    def testLotSize(self):
        self.assertRaises(InvalidSize, self.c1.checkOrder(self.o2_INVALID_SIZE))

    def testPositionCheck(self):
        self.assertRaises(PositionCheck, self.c1.checkOrder(self.o1))

    def testWorkingTrade(self):
        expected = ''
        self.BOOK.process_order()
        self.assertEqual(self.BOOK.show_book(), expected)

    def testRatingPriority(self):
        expected = ''
        self.BOOK.process_order()
        self.assertEqual(self.BOOK.show_book(), expected)

    def testTimePriority(self):
        expected = ''
        self.BOOK.process_order()
        self.assertEqual(self.BOOK.show_book(), expected)


if __name__ == '__main__':
    unittest.main()