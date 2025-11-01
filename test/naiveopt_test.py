from datetime import datetime, timedelta
import time
import tracemalloc
from pathlib import Path

from trading_lib.models import MarketDataPoint
from trading_lib.engine import ExecutionEngine
from trading_lib.portfolio import Portfolio
from trading_lib.models import RecordingInterval
from trading_lib.data_loader import load_market_data

from  Assignment3.strategies import NaiveMovingAverageStrategy, OptimizedMovingAverageStrategy

def test_naive_ma():
    # Use smaller windows for testing
    strategy = NaiveMovingAverageStrategy(short_window=3, long_window=5, quantity=100)
    
    # Create price data that will generate a buy signal
    # Start with declining prices, then rising prices to create MA crossover
    ticks = []
    base_time = datetime(2025, 1, 1, 10, 0, 0)
    
    # First 5 prices: declining trend (long MA will be higher)
    prices = [100, 99, 98, 97, 96]
    for i, price in enumerate(prices):
        ticks.append(MarketDataPoint(timestamp=base_time + timedelta(seconds=i), symbol="AAPL", price=price))
    
    # Next 3 prices: rising trend (short MA will catch up and cross above long MA)
    prices = [97, 98, 99]
    for i, price in enumerate(prices):
        ticks.append(MarketDataPoint(timestamp=base_time + timedelta(seconds=i+5), symbol="AAPL", price=price))
    
    # Add a few more prices to ensure we have enough for MA calculation
    prices = [100, 101, 102]
    for i, price in enumerate(prices):
        ticks.append(MarketDataPoint(timestamp=base_time + timedelta(seconds=i+8), symbol="AAPL", price=price))
    
    for tick in ticks:
        signals = strategy.generate_signals(tick)
        print(tick, signals)

def test_opt_ma():
    # Use smaller windows for testing
    strategy = OptimizedMovingAverageStrategy(short_window=3, long_window=5, quantity=100)
    
    # Create price data that will generate a buy signal
    # Start with declining prices, then rising prices to create MA crossover
    ticks = []
    base_time = datetime(2025, 1, 1, 10, 0, 0)
    
    # First 5 prices: declining trend (long MA will be higher)
    prices = [100, 99, 98, 97, 96]
    for i, price in enumerate(prices):
        ticks.append(MarketDataPoint(timestamp=base_time + timedelta(seconds=i), symbol="AAPL", price=price))
    
    # Next 3 prices: rising trend (short MA will catch up and cross above long MA)
    prices = [97, 98, 99]
    for i, price in enumerate(prices):
        ticks.append(MarketDataPoint(timestamp=base_time + timedelta(seconds=i+5), symbol="AAPL", price=price))
    
    # Add a few more prices to ensure we have enough for MA calculation
    prices = [100, 101, 102]
    for i, price in enumerate(prices):
        ticks.append(MarketDataPoint(timestamp=base_time + timedelta(seconds=i+8), symbol="AAPL", price=price))
    
    for tick in ticks:
        signals = strategy.generate_signals(tick)
        print(tick, signals)


def test_performance_100k():
    """Verify optimized strategy meets performance requirements."""
    data_path = Path("data/market_data_100k.csv")
    if not data_path.exists():
        raise ValueError(f"{data_path} not found")
    
    ticks = (load_market_data(data_path))
    strategy = OptimizedMovingAverageStrategy(quantity=100)
    portfolio = Portfolio(cash=100000)
    engine = ExecutionEngine(strategy, portfolio, failure_rate=0.0, recording_interval=RecordingInterval.TICK)
    
    tracemalloc.start()
    start_time = time.time()
    engine.process_ticks(ticks)
    elapsed_time = time.time() - start_time
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    peak_mb = peak / (1024 * 1024)
    
    assert elapsed_time < 1.0, f"Time {elapsed_time:.3f}s exceeds 1.0s threshold"
    assert peak_mb < 100, f"Memory {peak_mb:.2f}MB exceeds 100MB threshold"

if __name__ == "__main__":
    print("Testing Naive Moving Average Strategy")
    test_naive_ma()
    print("\nTesting Optimized Moving Average Strategy")
    test_opt_ma()