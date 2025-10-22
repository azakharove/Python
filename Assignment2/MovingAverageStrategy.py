from typing import Dict, List

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

    def generate_signals(self, tick: MarketDataPoint) -> list[tuple]:
        if tick.symbol not in self._prices:
            self._prices[tick.symbol] = [tick.price]
            return []
        
        self._prices[tick.symbol].append(tick.price)
        
        # Wait for enough prices to calculate moving averages
        if len(self._prices[tick.symbol]) < self.long_window:
            return []
        
        # Keep only the last long_window prices for memory efficiency
        self._prices[tick.symbol] = self._prices[tick.symbol][-self.long_window:]
        
        short_ma = sum(self._prices[tick.symbol][-self.short_window:]) / self.short_window
        long_ma = sum(self._prices[tick.symbol][-self.long_window:]) / self.long_window
        
        if short_ma > long_ma:
            return [(tick.symbol, self.quantity, tick.price, Action.BUY)]
        else:
            return []