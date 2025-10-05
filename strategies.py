from datetime import datetime
from dataclasses import dataclass  
import random
import unittest
from models import MarketDataPoint, Order
from abc import ABC, abstractmethod

class Strategy(ABC):
    "Enforces a common interface for trading strategies by defining methods "
    "that all subclasses must implement."
    @abstractmethod
    def generate_signals(self, tick: MarketDataPoint) -> list:
        pass

class MovingAverageCrossoverStrategy(Strategy):
    "Analyses short-term and long-term moving averages to generate buy/sell signals."
    

class MomentumStrategy(Strategy):
    pass