import unittest
import strategies
from models import MarketDataPoint, Order
from datetime import datetime

class TestStrategies(unittest.TestCase):
    def test_moving_avg_crossover(self):
        strategy = strategies.MovingAverageCrossoverStrategy(short_window=3, long_window=5, quantity=10)
        ticks = [
            MarketDataPoint(timestamp=datetime(year=2025, month=9, day=21, hour=19, minute=54, second=1), symbol="AAPL", price=100),
            MarketDataPoint(timestamp=datetime(year=2025, month=9, day=21, hour=19, minute=54, second=2), symbol="AAPL", price=101),
            MarketDataPoint(timestamp=datetime(year=2025, month=9, day=21, hour=19, minute=54, second=3), symbol="AAPL", price=102),
            MarketDataPoint(timestamp=datetime(year=2025, month=9, day=21, hour=19, minute=54, second=4), symbol="AAPL", price=106),
            MarketDataPoint(timestamp=datetime(year=2025, month=9, day=21, hour=19, minute=54, second=5), symbol="AAPL", price=108),
            MarketDataPoint(timestamp=datetime(year=2025, month=9, day=21, hour=19, minute=54, second=6), symbol="AAPL", price=110)
        ]
        signals = []
        for tick in ticks:
            signals.extend(strategy.generate_signals(tick))
        
        self.assertEqual(len(signals), 2)
        self.assertEqual(signals[0], ("AAPL", 10, 108, "BUY"))
        self.assertEqual(signals[1], ("AAPL", 0, 110, "HOLD"))

if __name__ == "__main__":
    unittest.main()