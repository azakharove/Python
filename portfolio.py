# list of products and quantities as dict in instructions {'AAPL': {'quantity': 0, 'avg_price': 0.0}}
# and cash amount
# to update quantity or cash, high level method that says update quant, product, and method update cash
# method that applies an executed order to the portfolio that applies functions ^ at once
# have default parameters cash = 0, dict = {}
from models import Order

class Portfolio:
    def __init__(self, cash: float = 0, holdings: dict = {}):
        self.cash = cash
        self.__holdings = holdings  # {'AAPL': {'quantity': 0, 'avg_price': 0.0}}

    def update_cash(self, amount: float):
        self.cash += amount
        if self.cash < 0:
            raise ValueError("Insufficient cash in portfolio")
        
    def add_to_holding(self, symbol: str, quantity: int, price: float):
        if symbol not in self.__holdings:
            self.__holdings[symbol] = {'quantity': 0, 'avg_price': 0.0}
        
        holding = self.__holdings[symbol]
        new_quantity = holding['quantity'] + quantity
        if new_quantity < 0:
            raise ValueError("Cannot sell more than currently held")
        elif new_quantity == 0:
            del self.__holdings[symbol]
        else:
            # only update average price if buying
            if quantity > 0:  # Buying
                total_cost = holding['avg_price'] * holding['quantity'] + price * quantity
                holding['avg_price'] = total_cost / new_quantity

            holding['quantity'] = new_quantity

    def apply_order(self, order: Order):
        if order.status != "COMPLETED":
            raise ValueError("Only completed orders can be applied to the portfolio")
        
        total_cost = order.price * order.quantity
        self.update_cash(-total_cost)
        self.add_to_holding(order.symbol, order.quantity, order.price)

    def get_holding(self, symbol: str):
        holding = self.__holdings.get(symbol, {'quantity': 0, 'avg_price': 0.0})
        return {'quantity': holding['quantity'], 'avg_price': holding['avg_price']}
