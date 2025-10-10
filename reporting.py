from typing import List, Dict
import statistics

from models import MarketDataPoint
from portfolio import Portfolio


def get_stock_value(symbol, ticks: List[MarketDataPoint]):
    """Find the most recent tick for the given symbol."""
    # Note: Both reversed() and filter() are lazy iterators, so next() stops at first match
    final_tick = next(filter(lambda tick: tick.symbol == symbol, reversed(ticks)), None)
    
    if final_tick is None:
        raise ValueError(f"No ticks found for symbol: {symbol}")
    
    return final_tick.price


def calculate_sharpe_ratio() -> float:
    """Placeholder for Sharpe ratio - requires periodic returns."""
    pass


def calculate_max_drawdown() -> float:
    """Placeholder for max drawdown - requires periodic values."""
    pass


def report_performance(portfolio: Portfolio, starting_cash: float, ticks: List[MarketDataPoint]) -> Dict:
    """Calculate performance metrics without exposing periodic returns."""
    holdings = portfolio.get_all_holdings()
    current_prices = {symbol: get_stock_value(symbol, ticks) for symbol in holdings.keys()}
    final_value = portfolio.get_portfolio_value(current_prices)
    
    # Total return
    total_return = (final_value - starting_cash) / starting_cash * 100 if starting_cash != 0 else 0.0
    pnl = final_value - starting_cash
    
    # Placeholder for periodic metrics
    sharpe_ratio = calculate_sharpe_ratio()
    max_drawdown = calculate_max_drawdown()
    
    return {
        "total_return": total_return,
        "pnl": pnl,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "final_value": final_value,
        "starting_value": starting_cash
    }
