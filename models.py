from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


@dataclass(frozen=True)
class MarketDataPoint:
    """Frozen dataclass representing a market data point."""

    timestamp: datetime
    symbol: str
    price: float

class OrderStatus(StrEnum):
    """Enum representing the status of an order."""

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Order:
    """Mutable class representing a trade order."""

    def __init__(self, symbol: str, quantity: int, price: float, status: OrderStatus):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.status = status

class Action(StrEnum):
    """Enum representing the action of an order."""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
