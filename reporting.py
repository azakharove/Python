from typing import List, Dict
import statistics
from engine import ExecutionEngine

from models import MarketDataPoint
from portfolio import Portfolio


def calculate_max_drawdown(periodic_returns) -> float:
    """Calculate Sharpe ratio using periodic returns"""
    values = [value[1] for value in periodic_returns]
    equity = 1.0
    peak = values[0]
    max_dd = 0.0

    for value in values:
        if value > peak:
            peak = value
        drawdown = ((value - peak) / peak) * 100  # negative during declines
        if drawdown < max_dd:
            max_dd = drawdown

    return max_dd

def calculate_sharpe_ratio(periodic_returns) -> float:
    """Calculate Max Drawdown using periodic returns"""
    values = [value[1] for value in periodic_returns]
    mean = statistics.fmean(values)
    stddev = statistics.pstdev(values)
    if stddev == 0:
        return 0.0
    sharpe = mean / stddev
    return sharpe


def report_performance(portfolio: Portfolio, starting_cash: float, ticks: List[MarketDataPoint], current_prices: dict[str, float], periodic_returns) -> Dict:
    """Calculate performance metrics without exposing periodic returns."""
    final_value = portfolio.get_portfolio_value(current_prices)
    
    # Total return
    total_return = (final_value - starting_cash) / starting_cash * 100 if starting_cash != 0 else 0.0
    pnl = final_value - starting_cash
    
    sharpe_ratio = calculate_sharpe_ratio(periodic_returns)
    max_drawdown = calculate_max_drawdown(periodic_returns)
    
    return {
        "total_return": total_return,
        "pnl": pnl,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "final_value": final_value,
        "starting_value": starting_cash
    }
