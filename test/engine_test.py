from datetime import datetime

from engine import ExecutionEngine
from portfolio import Portfolio
import strategies
from models import MarketDataPoint


def test_moving_avg_crossover_strategy():
    strategy = strategies.MovingAverageCrossoverStrategy(
        short_window=3, long_window=5, quantity=10
    )
    ticks = [
        MarketDataPoint(
            timestamp=datetime(
                year=2025, month=9, day=21, hour=19, minute=54, second=1
            ),
            symbol="AAPL",
            price=100,
        ),
        MarketDataPoint(
            timestamp=datetime(
                year=2025, month=9, day=21, hour=19, minute=54, second=2
            ),
            symbol="AAPL",
            price=101,
        ),
        MarketDataPoint(
            timestamp=datetime(
                year=2025, month=9, day=21, hour=19, minute=54, second=3
            ),
            symbol="AAPL",
            price=102,
        ),
        MarketDataPoint(
            timestamp=datetime(
                year=2025, month=9, day=21, hour=19, minute=54, second=4
            ),
            symbol="AAPL",
            price=106,
        ),
        MarketDataPoint(
            timestamp=datetime(
                year=2025, month=9, day=21, hour=19, minute=54, second=5
            ),
            symbol="AAPL",
            price=108,
        ),
        MarketDataPoint(
            timestamp=datetime(
                year=2025, month=9, day=21, hour=19, minute=54, second=6
            ),
            symbol="AAPL",
            price=110,
        ),
    ]

    portfolio = Portfolio(holdings={}, cash=10000)
    engine = ExecutionEngine(strategies=[strategy], portfolio=portfolio)
    engine.process_ticks(ticks)
    assert portfolio.cash == 8920
    assert portfolio.get_holding("AAPL") == {"quantity": 10, "avg_price": 108.0}
