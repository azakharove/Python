from typing import Dict, List
from datetime import datetime, timedelta

from trading_lib.strategy import Strategy
from trading_lib.models import MarketDataPoint, Action
import statistics

class VolatilityBreakoutStrategy(Strategy):
    """
    Buy if daily return > rolling 20-day volatility
    """
    def __init__(self, window: int = 20, quantity: int = 100):
        super().__init__(quantity)
        self.window = window
        self.volatility_history: Dict[str, List[float]] = {}
        self._prices: Dict[str, List[float]] = {}

    def _calculate_volatility(self, prices: List[float]) -> float:
        if len(prices) < self.window:
            return 0.0
        
        returns = [(prices[i] / prices[i - 1]) - 1 for i in range(1, len(prices))]

        return statistics.stdev(returns)

    def generate_signals(self, tick: MarketDataPoint) -> list[tuple]:
        sym, price = tick.symbol, tick.price
        
        if sym not in self._prices:
            self._prices[sym] = [price]
            self.volatility_history[sym] = []
            return []
        
        prev_prices = self._prices[sym]     

        if len(prev_prices) < self.window + 1:
            self._prices[sym].append(price)          
            return []
        
        rolling_vol = self._calculate_volatility(prev_prices)

        current_return = (price / prev_prices[-1]) - 1
        
        signals = []
        if current_return > rolling_vol:
            signals.append((sym, self.quantity, price, Action.BUY))

        prev_prices.append(price)

        self._prices[sym] = prev_prices[-(self.window + 1):]
        self.volatility_history[sym].append(rolling_vol)
        
        return signals
    
if __name__ == "__main__":
    # Use smaller window for testing
    strategy = VolatilityBreakoutStrategy(window=5, quantity=100)
    
    # Create price data that will generate a buy signal
    # Need: current_return > rolling_volatility
    ticks = []
    base_time = datetime(2025, 1, 1, 10, 0, 0)
    
    # First 6 prices: small, consistent changes to establish low volatility
    prices = [100, 100.1, 100.2, 100.3, 100.4, 100.5]
    for i, price in enumerate(prices):
        ticks.append(MarketDataPoint(timestamp=base_time + timedelta(seconds=i), symbol="AAPL", price=price))
    
    # Next price: big jump to create high return > low volatility
    prices = [101.5]  # Big jump from 100.5 to 101.5 (1% return)
    for i, price in enumerate(prices):
        ticks.append(MarketDataPoint(timestamp=base_time + timedelta(seconds=i+6), symbol="AAPL", price=price))
    
    for tick in ticks:
        signals = strategy.generate_signals(tick)
        print(tick, signals)