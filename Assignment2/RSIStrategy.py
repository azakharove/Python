from typing import Dict, List
from datetime import datetime, timedelta

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
        sym, price = tick.symbol, tick.price

        if sym not in self._prices:
            self._prices[sym] = [price]
            return []
        
        prev_prices = self._prices[sym]
        
        if len(prev_prices) < self.window + 1:
            self._prices[sym].append(price)
            return []
        
        rsi = self._calculate_rsi(prev_prices)
        
        signals = []
        if rsi < 30:
            signals.append((sym, self.quantity, price, Action.BUY))
        
        prev_prices.append(price)

        self._prices[sym] = prev_prices[-(self.window + 1):]
        
        return signals
        


if __name__ == "__main__":
    # Use smaller window for testing
    strategy = RSIStrategy(window=5, quantity=100)
    
    # Create price data that will generate a buy signal (oversold condition)
    # RSI < 30 means the stock is oversold, so we need declining prices
    ticks = []
    base_time = datetime(2025, 1, 1, 10, 0, 0)
    
    # Create declining prices to generate low RSI (oversold condition)
    # Start high, then decline consistently to create oversold RSI
    prices = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55]
    for i, price in enumerate(prices):
        ticks.append(MarketDataPoint(timestamp=base_time + timedelta(seconds=i), symbol="AAPL", price=price))
    
    for tick in ticks:
        signals = strategy.generate_signals(tick)
        print(tick, signals)