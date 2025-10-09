import random

from models import Action, MarketDataPoint, Order, OrderStatus
from portfolio import Portfolio
from strategies import Strategy
from exceptions import ExecutionError, OrderError


class ExecutionEngine:
    """Executes trading strategies by processing market data and managing orders.

    Processing flow:
    1. Iterate through MarketDataPoint objects in timestamp order
    2. For each tick, invoke strategies to generate signals
    3. Instantiate and validate Order objects from signals
    4. Execute orders by updating the portfolio
    """

    def __init__(
        self, strategies: list[Strategy], portfolio: Portfolio, failure_rate: float = 0.05
    ):
        self.strategies = strategies
        self.portfolio = portfolio
        self.failure_rate = failure_rate  # Simulate 5% failure rate by default

    def process_tick(self, tick: MarketDataPoint):
        for strategy in self.strategies:
            try:
                signals = strategy.generate_signals(tick)
                for symbol, quantity, price, action in signals:
                    if action != Action.HOLD:
                        order = Order(
                            symbol,
                            quantity,
                            price,
                            status=OrderStatus.PENDING,
                        )
                        self.execute_order(order)
            except Exception as e:
                print(f"Error processing tick {tick} with strategy {strategy}: {e}")

    def process_ticks(self, ticks: list[MarketDataPoint]):
        ticks.sort(key=lambda x: x.timestamp)  # Ensure ticks are in timestamp order

        for tick in ticks:
            self.process_tick(tick)

    def execute_order(self, order: Order):
        try:
            # Validate order status
            if order.status != OrderStatus.PENDING:
                raise OrderError(order, "Order must be PENDING to execute")

            # Check if portfolio can execute this order (sufficient cash/holdings)
            if not self.portfolio.can_execute_order(order):
                reason = "Insufficient cash" if order.quantity > 0 else "Insufficient holdings"
                raise OrderError(order, reason)

            # Simulate occasional execution failures 
            if random.random() < self.failure_rate:
                raise ExecutionError(order, "Simulated execution failure")

            # Execute order
            order.status = OrderStatus.COMPLETED
            self.portfolio.apply_order(order)
            print(
                f"Executed order: {order.symbol}, Quantity: {order.quantity}, Price: {order.price}, Status: {order.status}"
            )

        except ExecutionError as e:
            # Log execution failures but continue processing
            print(e)
            order.status = OrderStatus.FAILED

        except OrderError as e:
            print(e)
            order.status = OrderStatus.FAILED
