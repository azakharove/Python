from typing import Dict, List
from datetime import datetime, timedelta

from trading_lib.strategy import Strategy
from trading_lib.models import MarketDataPoint, Action

class MovingAverageStrategy(Strategy):
    """
    Buys if 20-day MA > 50-day MA
    """

    def __init__(self, short_window: int = 20, long_window: int = 50, quantity: int = 100):
        super().__init__(quantity)
        self.short_window = short_window
        self.long_window = long_window
        self._prices: Dict[str, List[float]] = {}
        # track previous MA relationship to catch true crossovers
        self._prev_short_gt_long: Dict[str, bool] = {}

    def generate_signals(self, tick: MarketDataPoint) -> list[tuple]:
        sym, price = tick.symbol, tick.price
        
        if sym not in self._prices:
            self._prices[sym] = [price]
            self._prev_short_gt_long[sym] = False
            return []
        
        prev_prices = self._prices[sym]
        
        # Wait for enough prices to calculate moving averages
        if len(prev_prices) < self.long_window:
            self._prices[sym].append(price)
            return []
        
        short_ma = sum(prev_prices[-self.short_window:]) / self.short_window
        long_ma = sum(prev_prices[-self.long_window:]) / self.long_window
        
        prev_state = self._prev_short_gt_long[sym]
        curr_state = short_ma > long_ma

        signals = []
        # trigger only on transition from False -> True (crossover up)
        if (not prev_state) and curr_state:
            signals.append((sym, self.quantity, price, Action.BUY))
        
        self._prev_short_gt_long[sym] = curr_state

        prev_prices.append(price)
        self._prices[sym] = prev_prices[-self.long_window:]  # long_window is enough
        
        return signals


if __name__ == "__main__":
    # Use smaller windows for testing
    strategy = MovingAverageStrategy(short_window=3, long_window=5, quantity=100)
    
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