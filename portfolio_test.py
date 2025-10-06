import unittest
from portfolio import Portfolio
from models import Order

class TestPortfolio(unittest.TestCase):
    def test_update_cash(self):
        portfolio = Portfolio()
        portfolio.update_cash(10000)
        self.assertEqual(portfolio.cash, 10000)

        portfolio.update_cash(-3000)
        self.assertEqual(portfolio.cash, 7000)

    def test_add_to_holding(self):
        portfolio = Portfolio(cash = 10000)
        portfolio.add_to_holding("AAPL", 10, 150)
        self.assertEqual(portfolio.get_holding("AAPL"), {'quantity': 10, 'avg_price': 150.0})
        portfolio.add_to_holding("AAPL", 30, 100)
        self.assertEqual(portfolio.get_holding("AAPL"), {'quantity': 40, 'avg_price': 112.5})
        portfolio.add_to_holding("AAPL", -20, 200)
        self.assertEqual(portfolio.get_holding("AAPL"), {'quantity': 20, 'avg_price': 112.5})

    def test_missing_holding(self):
        portfolio = Portfolio()
        self.assertEqual(portfolio.get_holding("MSFT"), {'quantity': 0, 'avg_price': 0.0})

    def test_apply_order(self):
        portfolio = Portfolio(holdings = {}, cash = 10000)
        #portfolio = Portfolio(cash = 10000) (ask)
        print(portfolio.get_holding("AAPL"))
        portfolio.apply_order(Order("AAPL", 10, 150, "COMPLETED"))
        self.assertEqual(portfolio.cash, 8500)
        self.assertEqual(portfolio.get_holding("AAPL"), {'quantity': 10, 'avg_price': 150.0})

        portfolio.apply_order(Order("AAPL", 30, 100, "COMPLETED"))
        self.assertEqual(portfolio.cash, 5500)
        self.assertEqual(portfolio.get_holding("AAPL"), {'quantity': 40, 'avg_price': 112.5})

        portfolio.apply_order(Order("AAPL", -20, 200, "COMPLETED"))
        self.assertEqual(portfolio.cash, 9500)
        self.assertEqual(portfolio.get_holding("AAPL"), {'quantity': 20, 'avg_price': 112.5})

        # with self.assertRaises(ValueError):
        #     pending_order = Order("AAPL", 5, 180, "PENDING")
        #     portfolio.apply_order(pending_order)

        # with self.assertRaises(ValueError):
        #     over_sell_order = Order("AAPL", 20, 180, "COMPLETED")
        #     portfolio.apply_order(over_sell_order)

    def test_apply_invalid_order(self):
        portfolio = Portfolio(cash = 10000)
        with self.assertRaises(ValueError):
            pending_order = Order("AAPL", 5, 180, "PENDING")
            portfolio.apply_order(pending_order)

    def test_sell_quantity_exceeds_holding(self):
        portfolio = Portfolio(holdings = {}, cash = 10000)
        portfolio.apply_order(Order("AAPL", 10, 150, "COMPLETED"))
        self.assertEqual(portfolio.cash, 8500)
        self.assertEqual(portfolio.get_holding("AAPL"), {'quantity': 10, 'avg_price': 150.0})
        with self.assertRaises(ValueError):
            portfolio.apply_order(Order("AAPL", -15, 150, "COMPLETED"))

    def test_sell_missing_holding(self):
        portfolio = Portfolio(holdings = {}, cash = 10000)
        with self.assertRaises(ValueError):
            portfolio.apply_order(Order("AAPL", -5, 150, "COMPLETED"))

if __name__ == "__main__":
    unittest.main()

