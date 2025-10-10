from models import Order, OrderStatus
from exceptions import OrderError


class Portfolio:
    """Portfolio management class for tracking cash and holdings.

    Holdings are stored as {'SYMBOL': {'quantity': int, 'avg_price': float}}
    """

    def __init__(self, cash: float = 0, holdings: dict = None):
        self.cash = cash
        self.__holdings = holdings if holdings is not None else {}

    def update_cash(self, amount: float):
        self.cash += amount
        if self.cash < 0:
            raise ValueError("Insufficient cash in portfolio")

    def add_to_holding(self, symbol: str, quantity: int, price: float):
        if symbol not in self.__holdings:
            self.__holdings[symbol] = {"quantity": 0, "avg_price": 0.0}

        holding = self.__holdings[symbol]
        new_quantity = holding["quantity"] + quantity
        if new_quantity < 0:
            raise OrderError(reason="Cannot sell more than currently held")
        elif new_quantity == 0:
            del self.__holdings[symbol]
        else:
            # only update average price if buying
            if quantity > 0:  # Buying
                total_cost = (
                    holding["avg_price"] * holding["quantity"] + price * quantity
                )
                holding["avg_price"] = total_cost / new_quantity

            holding["quantity"] = new_quantity

    def apply_order(self, order: Order):
        if order.status != OrderStatus.COMPLETED:
            raise OrderError(
                order, "Only completed orders can be applied to the portfolio"
            )

        total_cost = order.price * order.quantity
        self.update_cash(-total_cost)
        self.add_to_holding(order.symbol, order.quantity, order.price)

    def get_holding(self, symbol: str):
        holding = self.__holdings.get(symbol, {"quantity": 0, "avg_price": 0.0})
        return {"quantity": holding["quantity"], "avg_price": holding["avg_price"]}

    def can_execute_order(self, order: Order) -> bool:
        """Check if an order can be executed given current portfolio state.
        
        Returns True if:
        - For BUY orders: sufficient cash available
        - For SELL orders: sufficient holdings available
        """
        total_cost = order.price * order.quantity
        
        if order.quantity > 0:  # BUY order
            return self.cash >= total_cost
        else:  # SELL order
            holding = self.get_holding(order.symbol)
            return holding["quantity"] >= abs(order.quantity)
    
    def get_all_holdings(self):
        return {symbol: {"quantity": data["quantity"], "avg_price": data["avg_price"]} 
                for symbol, data in self.__holdings.items()}
    
    def get_holdings_value(self, current_prices: dict) -> float:
        return sum(
            holding["quantity"] * current_prices.get(symbol, holding["avg_price"])
            for symbol, holding in self.__holdings.items()
        )
    
    def get_cash(self) -> float:
        return self.cash

    def get_portfolio_value(self, current_prices: dict) -> float:
        return self.get_cash() + self.get_holdings_value(current_prices)
