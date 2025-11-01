from typing import Dict, List, Deque
from datetime import datetime, timedelta
from collections import deque

from trading_lib.strategy import Strategy
from trading_lib.models import MarketDataPoint, Action

class NaiveMovingAverageStrategy(Strategy):
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

        # Wait for enough prices to calculate moving averages
        if len(self._prices[sym]) < self.long_window:
            self._prices[sym].append(price)
            return []
        
        self._prices[sym].append(price)
        # creates a shallow copy of the last long_window prices
        self._prices[sym] = self._prices[sym][-self.long_window:]  # Keep only last long_window prices

        # sum all prices for each tick in the last short_window and long_window
        short_ma = sum(self._prices[sym][-self.short_window:]) / self.short_window
        long_ma = sum(self._prices[sym]) / self.long_window
        
        prev_state = self._prev_short_gt_long[sym]
        curr_state = short_ma > long_ma

        signals = []
        # trigger only on transition from False -> True (crossover up)
        if (not prev_state) and curr_state:
            signals.append((sym, self.quantity, price, Action.BUY))
        
        self._prev_short_gt_long[sym] = curr_state
        
        return signals
    
class OptimizedMovingAverageStrategy(Strategy):
    """
    Buys if 20-day MA > 50-day MA
    """

    def __init__(self, short_window: int = 20, long_window: int = 50, quantity: int = 100):
        super().__init__(quantity)
        self.short_window = short_window
        self.long_window = long_window
        self._prices: Dict[str, Deque[float]] = {}
        # track previous MA relationship to catch true crossovers
        self._prev_short_gt_long: Dict[str, bool] = {}
        # Per-symbol running sums
        self._short_sum: Dict[str, float] = {}
        self._long_sum: Dict[str, float] = {}

    def generate_signals(self, tick: MarketDataPoint) -> list[tuple]:
        sym, price = tick.symbol, tick.price
        
        if sym not in self._prices:
            # deque will maintain its length in place
            self._prices[sym] = deque(maxlen=self.long_window)
            self._prices[sym].append(price)
            self._prev_short_gt_long[sym] = False
            self._short_sum[sym] = price
            self._long_sum[sym] = price
            return []
        
        prices = self._prices[sym]

        # Wait for enough prices to calculate moving averages
        if len(prices) < self.long_window:
            prices.append(price)

            if len(prices) <= self.short_window:
                # Still building up to short_window
                self._short_sum[sym] += price
            else:
                # Already have >= short_window, maintain window size
                oldest_short = prices[-self.short_window - 1]
                self._short_sum[sym] = self._short_sum[sym] - oldest_short + price

            self._long_sum[sym] += price
            return []
        
        oldest_short = prices[-self.short_window]
        oldest_long = prices[0]

        prices.append(price)

        self._short_sum[sym] = self._short_sum[sym] - oldest_short + price
        self._long_sum[sym] = self._long_sum[sym] - oldest_long + price
        
        short_ma = self._short_sum[sym] / self.short_window
        long_ma = self._long_sum[sym] / self.long_window

        prev_state = self._prev_short_gt_long[sym]
        curr_state = short_ma > long_ma

        signals = []
        # trigger only on transition from False -> True (crossover up)
        if (not prev_state) and curr_state:
            signals.append((sym, self.quantity, price, Action.BUY))
        
        self._prev_short_gt_long[sym] = curr_state

        return signals