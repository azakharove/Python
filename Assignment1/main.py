from pathlib import Path
import sys
import argparse

from trading_lib.portfolio import Portfolio
from trading_lib.engine import ExecutionEngine
from trading_lib.reporting import generate_performance_report, report_performance
from trading_lib.models import RecordingInterval

# Local Assignment1 modules
sys.path.insert(0, str(Path(__file__).parent))
import data_loader
from strategies import MovingAverageCrossoverStrategy, MomentumStrategy

def parse_args(args):
    parser = argparse.ArgumentParser(description="Trading system")
    parser.add_argument('-d', "--csv_path", type=Path, default="data/market_data.csv")
    parser.add_argument('-q', "--quantity", type=int, default=10)
    parser.add_argument('-f', "--failure_rate", type=float, default=0.05)
    parser.add_argument('-c', "--cash", type=float, default=100000)
    parser.add_argument('-i', "--interval", type=str, default="1s",
                        choices=[e.value for e in RecordingInterval],
                        help="Portfolio recording interval (tick, 1s, 1m, 1h, 1d, 1mo)")

    return parser.parse_args(args)

def main(args):
    parsed_args = parse_args(args)
    csv_path = parsed_args.csv_path
    quantity = parsed_args.quantity
    failure_rate = parsed_args.failure_rate
    cash = parsed_args.cash
    interval = RecordingInterval(parsed_args.interval)
    
    # data_generator.generate_market_csv(csv_path)
    ticks = data_loader.load_market_data(csv_path)
    print(f"Loaded {len(ticks)} market data points.")
    
    strategies = [MovingAverageCrossoverStrategy(quantity=quantity), MomentumStrategy(quantity=quantity)]

    portfolio = Portfolio(cash=cash)
    engine = ExecutionEngine(strategies, portfolio, failure_rate, recording_interval=interval)
    engine.process_ticks(ticks)

    # Generate performance report
    current_prices = engine.get_current_prices()
    periodic_returns = engine.get_portfolio_history()
    metrics = report_performance(portfolio, cash, ticks, current_prices, periodic_returns)
    

    
    # Get holdings
    holdings = portfolio.get_all_holdings()
    holdings_value = metrics['final_value'] - portfolio.get_cash()
    
    print(f"\n{'='*60}")
    print(f"FINAL PORTFOLIO SUMMARY")
    print(f"{'='*60}")
    print(f"Initial capital:     ${metrics['starting_value']:,.2f}")
    print(f"Final cash:          ${portfolio.get_cash():,.2f}")
    print(f"Holdings value:      ${holdings_value:,.2f}")
    print(f"Total portfolio:     ${metrics['final_value']:,.2f}")
    print(f"P&L:                 ${metrics['pnl']:,.2f} ({metrics['total_return']:+.2f}%)")
    print(f"\n{'='*60}")
    print(f"PERFORMANCE METRICS")
    print(f"{'='*60}")
    print(f"Sharpe Ratio:        {metrics['sharpe_ratio']:.2f}")
    print(f"Max Drawdown:        {metrics['max_drawdown']:.2f}%")
    
    if holdings:
        print(f"\n{'='*60}")
        print(f"CURRENT HOLDINGS")
        print(f"{'='*60}")
        for symbol, holding in holdings.items():
            price = current_prices.get(symbol, 0)
            position_value = holding["quantity"] * price
            print(f"  {symbol}: {holding['quantity']} shares @ ${price:.2f} = ${position_value:,.2f}")

    # Generate performance report
    generate_performance_report(metrics, periodic_returns, output_file="performance.md")

if __name__ == "__main__":
    main(sys.argv[1:])
