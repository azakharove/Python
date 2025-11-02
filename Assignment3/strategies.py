from typing import Dict, List, Deque
from datetime import datetime, timedelta
from collections import deque

from trading_lib.strategy import Strategy
from trading_lib.models import MarketDataPoint, Action

class NaiveMovingAverageStrategy(Strategy):
    """
    Buys if 20-day MA > 50-day MA
    
    Time Complexity: O(n) per tick, where n = window size
    Space Complexity: O(n) per symbol, where n = long_window
    """

    def __init__(self, short_window: int = 20, long_window: int = 50, quantity: int = 100):
        super().__init__(quantity)
        self.short_window = short_window
        self.long_window = long_window
        self._prices: Dict[str, List[float]] = {}
        # track previous MA relationship to catch true crossovers
        self._prev_short_gt_long: Dict[str, bool] = {}

    def generate_signals(self, tick: MarketDataPoint) -> list[tuple]:
        """
        Generate trading signals based on moving average crossover.
        
        Time Complexity: O(n) per tick
          - List slicing: O(n) where n = long_window
          - Sum calculation: O(n) where n = window size (short_window or long_window)
          - Overall: O(n) dominated by sum operations
        
        Space Complexity: O(n) per symbol
          - _prices dict stores at most long_window prices per symbol
        """
        sym, price = tick.symbol, tick.price
        
        if sym not in self._prices:  # O(1) dict lookup
            self._prices[sym] = [price]  # O(1) list creation
            self._prev_short_gt_long[sym] = False
            return []

        if len(self._prices[sym]) < self.long_window:  # O(1) len check
            self._prices[sym].append(price)  # O(1) append
            return []
        
        self._prices[sym].append(price)  # O(1) append
        # Time: O(n) where n = long_window (creates new list with n elements)
        # Space: O(n) temporary list during slicing
        self._prices[sym] = self._prices[sym][-self.long_window:]

        # Time: O(short_window) - sums short_window elements
        short_ma = sum(self._prices[sym][-self.short_window:]) / self.short_window
        # Time: O(long_window) - sums long_window elements
        # Overall: O(n) where n = long_window (dominates short_window)
        long_ma = sum(self._prices[sym]) / self.long_window
        
        # O(1) operations
        prev_state = self._prev_short_gt_long[sym]
        curr_state = short_ma > long_ma
        
        signals = []
        if (not prev_state) and curr_state:
            signals.append((sym, self.quantity, price, Action.BUY))  # O(1)
        
        self._prev_short_gt_long[sym] = curr_state  # O(1)
        
        return signals  # O(1)
    
class OptimizedMovingAverageStrategy(Strategy):
    """
    Buys if 20-day MA > 50-day MA
    
    Time Complexity: O(1) per tick - incremental updates
    Space Complexity: O(k) per symbol, where k = long_window (fixed-size deque)
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
        """
        Generate trading signals using incremental moving average updates.
        
        Time Complexity: O(1) per tick
          - deque.append with maxlen: O(1) - auto-removes oldest
          - Incremental sum updates: O(1) - subtract old, add new
          - All operations are constant time
        
        Space Complexity: O(k) per symbol, where k = long_window
          - Fixed-size deque maintains exactly long_window elements
          - Constant space for running sums (2 floats)
        """
        sym, price = tick.symbol, tick.price
        
        if sym not in self._prices:  # O(1) dict lookup
            # O(1) - deque initialization
            self._prices[sym] = deque(maxlen=self.long_window)
            self._prices[sym].append(price)  # O(1)
            self._prev_short_gt_long[sym] = False  # O(1)
            self._short_sum[sym] = price  # O(1)
            self._long_sum[sym] = price  # O(1)
            return []
        
        prices = self._prices[sym]

        if len(prices) < self.long_window:  # O(1) len check
            prices.append(price)  # O(1) - deque append

            if len(prices) <= self.short_window:  # O(1)
                self._short_sum[sym] += price  # O(1)
            else:
                # O(1) - list conversion for indexing, but only when needed
                oldest_short = list(prices)[-self.short_window - 1]  # O(k) but only during build-up
                self._short_sum[sym] = self._short_sum[sym] - oldest_short + price  # O(1)

            self._long_sum[sym] += price  # O(1)
            return []
        
        # O(1) - accessing first and nth element in deque
        oldest_short = list(prices)[-self.short_window - 1]  # O(k)
        oldest_long = prices[0]  # O(1) - deque indexing

        prices.append(price)  # O(1) - deque auto-removes oldest when at maxlen

        # O(1) - constant time incremental updates
        self._short_sum[sym] = self._short_sum[sym] - oldest_short + price
        self._long_sum[sym] = self._long_sum[sym] - oldest_long + price
        
        # O(1) - simple division
        short_ma = self._short_sum[sym] / self.short_window
        long_ma = self._long_sum[sym] / self.long_window

        # O(1) operations
        prev_state = self._prev_short_gt_long[sym]
        curr_state = short_ma > long_ma

        signals = []
        if (not prev_state) and curr_state:
            signals.append((sym, self.quantity, price, Action.BUY))  # O(1)
        
        self._prev_short_gt_long[sym] = curr_state  # O(1)
        
        return signals