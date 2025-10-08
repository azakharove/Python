from datetime import datetime
import dataclasses as dataclass

import pytest

from models import MarketDataPoint, Order


def test_immutable():
    timenow = datetime.now()
    mdp = MarketDataPoint(timenow, "AAPL", 100.0)

    assert mdp.symbol == "AAPL"
    assert mdp.price == 100.0
    assert mdp.timestamp == timenow

    with pytest.raises(dataclass.FrozenInstanceError):
        mdp.price = 150.0
    with pytest.raises(dataclass.FrozenInstanceError):
        mdp.symbol = "ABCD"
    with pytest.raises(dataclass.FrozenInstanceError):
        mdp.timestamp = "2024-09-21T19:54:02.109914"


def test_mutable():
    order = Order("APPL", 100, 100, "PENDING")
    
    order.symbol = "ABCD"
    assert order.symbol == "ABCD"
    
    order.quantity = 200
    assert order.quantity == 200
    
    order.price = 150.0
    assert order.price == 150.0
    
    order.status = "COMPLETED"
    assert order.status == "COMPLETED"
