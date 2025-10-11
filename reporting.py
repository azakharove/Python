from typing import List, Dict
import statistics

from models import MarketDataPoint
from portfolio import Portfolio


def calculate_sharpe_ratio() -> float:
    """Placeholder for Sharpe ratio - requires periodic returns."""
    pass


def calculate_max_drawdown() -> float:
    """Placeholder for max drawdown - requires periodic values."""
    pass


def report_performance(portfolio: Portfolio, starting_cash: float, ticks: List[MarketDataPoint], current_prices: dict[str, float]) -> Dict:
    """Calculate performance metrics without exposing periodic returns."""
    final_value = portfolio.get_portfolio_value(current_prices)
    
    # Total return
    total_return = (final_value - starting_cash) / starting_cash * 100 if starting_cash != 0 else 0.0
    pnl = final_value - starting_cash
    
    # Placeholder for periodic metrics
    # sharpe_ratio = calculate_sharpe_ratio()
    # max_drawdown = calculate_max_drawdown()
    
    return {
        "total_return": total_return,
        "pnl": pnl,
        "sharpe_ratio": 0,
        "max_drawdown": 0,
        "final_value": final_value,
        "starting_value": starting_cash
    }
