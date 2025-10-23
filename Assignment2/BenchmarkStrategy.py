from trading_lib.strategy import Strategy
from trading_lib.models import MarketDataPoint, Action
from typing import Set
from datetime import datetime, timedelta

class BenchmarkStrategy(Strategy):
    """
    Buys and holds all stocks indefinitely.
    """
    def __init__(self, quantity: int = 100):
        super().__init__(quantity)
        self._symbols: Set[str] = set()
    
    def generate_signals(self, tick: MarketDataPoint) -> list[tuple]:
        """
        Buy each stock only once on the first tick we see for that symbol.
        """
        if tick.symbol not in self._symbols:
            self._symbols.add(tick.symbol)
            return [(tick.symbol, self.quantity, tick.price, Action.BUY)]
        
        # Already bought this stock
        return []


if __name__ == "__main__":
    strategy = BenchmarkStrategy(quantity=100)
    
    # Create test data with multiple symbols to show buy-and-hold behavior
    ticks = []
    base_time = datetime(2025, 1, 1, 10, 0, 0)
    
    # Create multiple symbols with multiple ticks each
    symbols = ["AAPL", "MSFT", "GOOGL"]
    prices = [100, 101, 102, 103, 104, 105]
    
    for symbol in symbols:
        for i, price in enumerate(prices):
            ticks.append(MarketDataPoint(timestamp=base_time + timedelta(seconds=i), symbol=symbol, price=price))
    
    for tick in ticks:
        signals = strategy.generate_signals(tick)
        print(tick, signals)