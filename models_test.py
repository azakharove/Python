from models import MarketDataPoint, Order
from datetime import datetime
import unittest
import dataclasses as dataclass

class TestMarketDataPoint(unittest.TestCase):
    def test_immutable(self):
        timenow = datetime.now()
        mdp = MarketDataPoint(timenow, "AAPL", 100.0)
        self.assertEqual(mdp.symbol, "AAPL")
        self.assertEqual(mdp.price, 100.0)
        self.assertEqual(mdp.timestamp, timenow)
        with self.assertRaises(dataclass.FrozenInstanceError):
            mdp.price = 150.0
        with self.assertRaises(dataclass.FrozenInstanceError):
            mdp.symbol = "ABCD"
        with self.assertRaises(dataclass.FrozenInstanceError):
            mdp.timestamp = "2024-09-21T19:54:02.109914"     

class TestOrder(unittest.TestCase):
    def test_mutable(self):
        order = Order("APPL", 100, 100, "PENDING")
        order.symbol = "ABCD"
        self.assertEqual(order.symbol, "ABCD")
        order.quantity = 200
        self.assertEqual(order.quantity, 200)
        order.price = 150.0
        self.assertEqual(order.price, 150.0)
        order.status = "COMPLETED"
        self.assertEqual(order.status, "COMPLETED")

if __name__ == "__main__":
    unittest.main()