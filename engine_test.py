from engine import ExecutionEngine
import unittest
from portfolio import Portfolio
import strategies
from models import MarketDataPoint
from datetime import datetime

class TestExecutionEngine(unittest.TestCase):
    def test_moving_avg_crossover_strategy(self):
        strategy = strategies.MovingAverageCrossoverStrategy(short_window=3, long_window=5, quantity=10)
        ticks = [
            MarketDataPoint(timestamp=datetime(year=2025, month=9, day=21, hour=19, minute=54, second=1), symbol="AAPL", price=100),
            MarketDataPoint(timestamp=datetime(year=2025, month=9, day=21, hour=19, minute=54, second=2), symbol="AAPL", price=101),
            MarketDataPoint(timestamp=datetime(year=2025, month=9, day=21, hour=19, minute=54, second=3), symbol="AAPL", price=102),
            MarketDataPoint(timestamp=datetime(year=2025, month=9, day=21, hour=19, minute=54, second=4), symbol="AAPL", price=106),
            MarketDataPoint(timestamp=datetime(year=2025, month=9, day=21, hour=19, minute=54, second=5), symbol="AAPL", price=108),
            MarketDataPoint(timestamp=datetime(year=2025, month=9, day=21, hour=19, minute=54, second=6), symbol="AAPL", price=110)
        ]

        portfolio = Portfolio(holdings = {}, cash=10000)
        engine = ExecutionEngine(strategies=[strategy], portfolio=portfolio)
        engine.process_ticks(ticks)
        self.assertEqual(portfolio.cash, 8920)
        self.assertEqual(portfolio.get_holding("AAPL"), {'quantity': 10, 'avg_price': 108.0})

if __name__ == "__main__":
    unittest.main()
