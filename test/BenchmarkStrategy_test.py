from datetime import datetime, timedelta

from Assignment2.BenchmarkStrategy import BenchmarkStrategy
from trading_lib.models import Action, MarketDataPoint

def test_benchmark_strategy():
    strategy = BenchmarkStrategy(quantity=50)

    # Create test data with multiple symbols to show buy-and-hold behavior
    ticks = []
    base_time = datetime(2025, 1, 1, 10, 0, 0)
    
    # Create multiple symbols with multiple ticks each
    symbols = ["AAPL", "MSFT", "GOOGL"]
    prices = [100, 101, 102, 103, 104, 105]
    price_delta = 0
    for symbol in symbols:
        for i, price in enumerate(prices):
            ticks.append(MarketDataPoint(timestamp=base_time + timedelta(seconds=i), symbol=symbol, price=price + price_delta))
        price_delta += 10
    
    signals = []
    for tick in ticks:
        signals = signals + strategy.generate_signals(tick)

    assert len(signals) == 3
    assert signals[0] == ("AAPL", 50, 100, Action.BUY)
    assert signals[1] == ("MSFT", 50, 110, Action.BUY)
    assert signals[2] == ("GOOGL", 50, 120, Action.BUY)