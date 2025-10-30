from datetime import datetime, timedelta

from trading_lib.models import MarketDataPoint

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


if __name__ == "__main__":
    print("Testing Naive Moving Average Strategy")
    test_naive_ma()
    print("\nTesting Optimized Moving Average Strategy")
    test_opt_ma()