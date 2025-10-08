import strategies
from models import MarketDataPoint, Order
from portfolio import Portfolio


class ExecutionEngine:
    # Iterate through the list of MarketDataPoint objects in timestamp order.
    # For each tick:
    #   Invoke each strategy to generate signals.
    #   Instantiate and validate Order objects.
    #   Execute orders by updating the portfolio dictionary.
    # Wrap order creation and execution in try/except blocks for resilience.
    def __init__(self, strategies: list[strategies.Strategy], portfolio: Portfolio):
        self.strategies = strategies
        self.portfolio = portfolio

    def process_tick(self, tick: MarketDataPoint):
        for strategy in self.strategies:
            try:
                signals = strategy.generate_signals(tick)
                for signal in signals:
                    symbol, quantity, price, action = signal
                    if action != "HOLD":
                        order = Order(
                            symbol,
                            quantity if action == "BUY" else -quantity,
                            price,
                            status="PENDING",
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
            if order.status != "PENDING":
                raise ValueError("Order status must be PENDING to execute")

            # Simulate order execution

            order.status = "COMPLETED"
            self.portfolio.apply_order(order)
            print(
                f"Executed order: {order.symbol}, Quantity: {order.quantity}, Price: {order.price}, Status: {order.status}"
            )
        except Exception as e:
            print(f"Error executing order {order}: {e}")
