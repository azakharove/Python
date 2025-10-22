from trading_lib.strategy import Strategy
from trading_lib.models import MarketDataPoint, Action
from typing import Set

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