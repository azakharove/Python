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
    
    # Save BEFORE show, otherwise the figure will be cleared
    plt.savefig(file_name, dpi=300, bbox_inches='tight')
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
    return interpretation


def generate_performance_report(metrics, portfolio_history, output_file="performance.md"):
    """Generate a complete performance.md report with metrics, chart, and narrative."""
    
    # Generate equity curve plot
    chart_filename = "equity_curve.png"
    equity_curve_plot(portfolio_history, chart_filename)
    
    # Get narrative interpretation
    narrative = narrative_interpretation(metrics)
    
    # Build the markdown report
    report = f"""# Trading Strategy Performance Report

## Summary Metrics

| Metric | Value |
|--------|-------|
| Starting Value | ${metrics['starting_value']:,.2f} |
| Final Value | ${metrics['final_value']:,.2f} |
| Total Return | {metrics['total_return']:.2f}% |
| P&L | ${metrics['pnl']:,.2f} |
| Sharpe Ratio | {metrics['sharpe_ratio']:.2f} |
| Max Drawdown | {metrics['max_drawdown']:.2f}% |

## Equity Curve

![Equity Curve]({chart_filename})

## Performance Analysis

{narrative}

## Interpretation

### Sharpe Ratio ({metrics['sharpe_ratio']:.2f})
"""
    
    if metrics['sharpe_ratio'] > 1.0:
        report += "- **Excellent**: Risk-adjusted returns are strong. The strategy generates good returns relative to volatility.\n"
    elif metrics['sharpe_ratio'] > 0.5:
        report += "- **Moderate**: Acceptable risk-adjusted returns, but there's room for improvement.\n"
    else:
        report += "- **Poor**: Returns don't justify the risk taken. Strategy needs refinement.\n"
    
    report += f"""
### Max Drawdown ({metrics['max_drawdown']:.2f}%)
"""
    
    if abs(metrics['max_drawdown']) < 10:
        report += "- **Low**: Excellent risk management with minimal losses from peak.\n"
    elif abs(metrics['max_drawdown']) < 20:
        report += "- **Moderate**: Acceptable drawdown levels, but consider risk mitigation strategies.\n"
    else:
        report += "- **High**: Significant losses from peak. Review risk management and position sizing.\n"
    
    report += f"""
### Total Return ({metrics['total_return']:.2f}%)
"""
    
    if metrics['total_return'] > 20:
        report += "- **Strong**: Strategy generated substantial profits.\n"
    elif metrics['total_return'] > 0:
        report += "- **Positive**: Strategy was profitable, though returns could be improved.\n"
    else:
        report += "- **Negative**: Strategy lost money. Requires significant adjustments.\n"
    
    report += "\n---\n*Report generated automatically from backtesting results*\n"
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"Performance report generated: {output_file}")
    return output_file