from typing import Dict, List

from trading_lib.strategy import Strategy
from trading_lib.models import MarketDataPoint, Action

class RSIStrategy(Strategy):
    """
    Buy if RSI < 30
    """
    def __init__(self, window: int = 14, quantity: int = 100):
        super().__init__(quantity)
        self.window = window
        self._prices: Dict[str, List[float]] = {}

    def _calculate_rsi(self, prices: List[float]) -> float:
        if len(prices) < self.window + 1:
            return 50.0  # Neutral RSI
        
        # Calculate gains and losses for the last window periods only
        gains = []
        losses = []
        
        for i in range(len(prices) - self.window, len(prices)):
            change = prices[i] - prices[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        # Calculate average gain and loss
        avg_gain = sum(gains) / len(gains)
        avg_loss = sum(losses) / len(losses)
        
        # Avoid division by zero
        if avg_loss == 0:
            return 100.0
        
        # Calculate RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signals(self, tick: MarketDataPoint) -> list[tuple]:
        if tick.symbol not in self._prices:
            self._prices[tick.symbol] = [tick.price]
            return []
        
        self._prices[tick.symbol].append(tick.price)

        if len(self._prices[tick.symbol]) < self.window + 1:
            return []
        
        self._prices[tick.symbol] = self._prices[tick.symbol][-(self.window + 1):]
        
        rsi = self._calculate_rsi(self._prices[tick.symbol])
        if rsi < 30:
            return [(tick.symbol, self.quantity, tick.price, Action.BUY)]
        else:
            return []