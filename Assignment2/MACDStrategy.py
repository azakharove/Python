from typing import Dict, List

from trading_lib.strategy import Strategy
from trading_lib.models import MarketDataPoint, Action
from datetime import datetime, timedelta

class MACDStrategy(Strategy):
    """
    Buy if MACD line crosses above signal line
    """
    def __init__(self, short_window: int = 12, long_window: int = 26, signal_window: int = 9, quantity: int = 100):
        super().__init__(quantity)
        self.short_window = short_window
        self.long_window = long_window
        self.signal_window = signal_window
        self._prices: Dict[str, List[float]] = {}
        self.macd_history: Dict[str, List[float]] = {}
        self._prev_macd: Dict[str, float] = {}
        self._prev_signal: Dict[str, float] = {}

    def _calculate_ema(self, prices: List[float], window: int) -> float:
        if len(prices) < window:
            return 0.0
        
        alpha = 2 / (window + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
        return ema
    
    def _calculate_macd(self, prices: List[float]) -> float:
        if len(prices) < self.long_window:
            return 0.0

        ema_short = self._calculate_ema(prices, self.short_window)
        ema_long = self._calculate_ema(prices, self.long_window)

        # MACD is the difference between the short and long EMA
        return ema_short - ema_long

    def _calculate_signal(self, macd: List[float]) -> float:
        if len(macd) < self.signal_window:
            return 0.0
        
        # Calculate the signal line as the EMA of the MACD
        return self._calculate_ema(macd, self.signal_window)

    def generate_signals(self, tick: MarketDataPoint) -> list[tuple]:
        sym, price = tick.symbol, tick.price
        
        if sym not in self._prices:
            self._prices[sym] = [price]
            self.macd_history[sym] = []
            self._prev_macd[sym] = 0.0
            self._prev_signal[sym] = 0.0
            return []
        

        self._prices[sym].append(price)
        
        if len(self._prices[sym]) < self.long_window:
            return []
        
        self._prices[sym] = self._prices[sym][-self.long_window:]
        
        macd = self._calculate_macd(self._prices[sym])
        self.macd_history[sym].append(macd)
        
        # Wait for enough MACD values to calculate the signal line
        if len(self.macd_history[sym]) < self.signal_window:
            return []
        
        
        signal = self._calculate_signal(self.macd_history[sym])
        
        # Only care about crosses above the signal line (no shorting)
        cross_above = macd > signal and self._prev_macd[sym] <= self._prev_signal[sym]
        
        signals = []
        # Buy if the MACD line crosses above the signal line
        if cross_above:
            signals.append((sym, self.quantity, price, Action.BUY))
        
        self._prev_macd[sym] = macd
        self._prev_signal[sym] = signal
        # Keep only the signal_window MACD values
        self.macd_history[sym] = self.macd_history[sym][-self.signal_window:]
        
        return signals
    

if __name__ == "__main__":
    # Use smaller windows for testing
    strategy = MACDStrategy(short_window=3, long_window=5, signal_window=3, quantity=100)
    
    # Create price data that will generate a buy signal
    # Start with declining prices, then rising prices to create MACD crossover
    ticks = []
    base_time = datetime(2025, 1, 1, 10, 0, 0)
    
    # First 5 prices: declining trend (slow EMA will be higher)
    prices = [100, 99, 98, 97, 96]
    for i, price in enumerate(prices):
        ticks.append(MarketDataPoint(timestamp=base_time + timedelta(seconds=i), symbol="AAPL", price=price))
    
    # Next 3 prices: rising trend (fast EMA will catch up and cross above slow EMA)
    prices = [97, 98, 99]
    for i, price in enumerate(prices):
        ticks.append(MarketDataPoint(timestamp=base_time + timedelta(seconds=i+5), symbol="AAPL", price=price))
    
    # Add a few more prices to ensure we have enough for signal line calculation
    prices = [100, 101, 102]
    for i, price in enumerate(prices):
        ticks.append(MarketDataPoint(timestamp=base_time + timedelta(seconds=i+8), symbol="AAPL", price=price))
    for tick in ticks:
        signals = strategy.generate_signals(tick)
        print(tick, signals)