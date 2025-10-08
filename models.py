from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MarketDataPoint:
    """Frozen dataclass representing a market data point."""

    timestamp: datetime
    symbol: str
    price: float


class Order:
    """Mutable class representing a trade order."""

    def __init__(self, symbol: str, quantity: int, price: float, status: str):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.status = status
