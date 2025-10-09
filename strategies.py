from abc import ABC, abstractmethod


from models import Action, MarketDataPoint


class Strategy(ABC):
    """Base class for trading strategies.

    Enforces a common interface for trading strategies by defining methods
    that all subclasses must implement.
    """

    def __init__(self, quantity: int = 100):
        super().__init__()
        self._prices = [] 
        self.quantity = quantity 

    @abstractmethod
    def generate_signals(self, tick: MarketDataPoint) -> list[tuple]:
        raise NotImplementedError("Subclasses must implement generate_signals method")


class MovingAverageCrossoverStrategy(Strategy):
    """Moving average crossover trading strategy.

    Analyzes short-term and long-term moving averages to generate buy/sell signals.
    Buy when short MA crosses above long MA, sell when crosses below.
    """

    def __init__(
        self, short_window: int = 20, long_window: int = 50, quantity: int = 100
    ):
        super().__init__(quantity=quantity)
        assert short_window < long_window and short_window > 0 and long_window > 0
        self.short_window = short_window
        self.long_window = long_window
        self.last_signal = None

    def generate_signals(self, tick: MarketDataPoint) -> list[tuple]:
        self._prices.append(tick.price)
        if len(self._prices) < self.long_window:
            return []

        short_ma = sum(self._prices[-self.short_window :]) / self.short_window
        long_ma = sum(self._prices[-self.long_window :]) / self.long_window

        signals = []

        if short_ma > long_ma and self.last_signal != Action.BUY:
            signals.append((tick.symbol, self.quantity, tick.price, Action.BUY))
            self.last_signal = Action.BUY
        elif short_ma < long_ma and self.last_signal != Action.SELL:
            signals.append((tick.symbol, -self.quantity, tick.price, Action.SELL))
            self.last_signal = Action.SELL
        else:
            signals.append((tick.symbol, 0, tick.price, Action.HOLD))

        return signals


class MomentumStrategy(Strategy):
    "Analyses price momentum to generate buy signals for upward trends and sell signals for downward trends."

    def __init__(
        self, lookback: int = 10, holding_period: int = 5, quantity: int = 100
    ):
        super().__init__(quantity=quantity)
        assert lookback > 0 and holding_period > 0
        self.lookback = lookback
        self.holding_period = holding_period
        self.hold = 0

    def generate_signals(self, tick: MarketDataPoint) -> list[tuple]:
        self._prices.append(tick.price)
        if len(self._prices) < self.lookback:
            return []

        momentum = tick.price - self._prices[-self.lookback]

        if self.holding_period > 0:
            self.holding_period -= 1
            return []

        signals = []

        if momentum > 0:
            signals.append((tick.symbol, self.quantity, tick.price, Action.BUY))
            self.hold = self.holding_period
        elif momentum < 0:
            signals.append((tick.symbol, -self.quantity, tick.price, Action.SELL))
            self.hold = self.holding_period
        else:
            signals.append((tick.symbol, 0, tick.price, Action.HOLD))

        return signals
