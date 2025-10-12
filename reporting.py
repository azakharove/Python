from typing import List, Dict
import statistics
import matplotlib.pyplot as plt
from engine import ExecutionEngine
from models import MarketDataPoint
from portfolio import Portfolio


def calculate_max_drawdown(periodic_returns) -> float:
    """Calculate Sharpe ratio using periodic"""
    values = [value[1] for value in periodic_returns]
    peak = values[0]
    max_dd = 0.0

    for value in values:
        if value > peak:
            peak = value
        drawdown = ((value - peak) / peak) * 100
        if drawdown < max_dd:
            max_dd = drawdown

    return max_dd

def calculate_sharpe_ratio(periodic_returns) -> float:
    """Calculate Max Drawdown using periodic returns"""
    values = [value[1] for value in periodic_returns]
    returns = [
        (values[i] - values[i - 1]) / values[i - 1]
        for i in range(1, len(values))
        if values[i - 1] != 0
    ]
    mean = statistics.fmean(returns)
    stddev = statistics.pstdev(returns)
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

def equity_curve_plot(portfolio_history, file_name = "equity_curve.png"):
    """Generate equity curve plot from portfolio history."""

    dates, values = zip(*portfolio_history)
    plt.figure(figsize=(10, 6))
    plt.plot(dates, values, label='Portfolio Value', color='blue')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value ($)')
    plt.title('Equity Curve')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    plt.savefig(file_name)
    plt.close()

    link = f"! [Equity Curve](Path{file_name}))"
    return link

def narrative_interpretation(metrics):
    """Generate a narrative interpretation of the performance metrics."""
    if metrics['sharpe_ratio'] > 1.0 and metrics['max_drawdown'] < 20.0:
        interpretation = (f"The strategy performed exceptionally well with a Sharpe ratio of {metrics['sharpe_ratio']:.2f}, "
                          f"returning a final portfolio value of ${metrics['final_value']:,.2f} while maintaining drawdowns of {metrics['max_drawdown']:.2f}%. "
                          "This indicates a strong risk-adjusted return and effective risk management.")
    elif metrics['sharpe_ratio'] > 0.5:
        interpretation = (f"The strategy showed decent performance with a Sharpe ratio of {metrics['sharpe_ratio']:.2f}, "
                          f"achieving a final portfolio value of ${metrics['final_value']:,.2f} and drawdowns of {metrics['max_drawdown']:.2f}%. "
                          "This suggests moderate volatility with room for improvement in risk management.")
    else:
        interpretation = (f"The strategy had a low Sharpe ratio of {metrics['sharpe_ratio']:.2f}, "
                          f"resulting in a final portfolio value of ${metrics['final_value']:,.2f} and drawdowns of {metrics['max_drawdown']:.2f}%. "
                          "This indicates that the returns were not sufficient to compensate for the risk taken, highlighting the need for strategy refinement.")
    print(interpretation)