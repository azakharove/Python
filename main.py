from pathlib import Path
import sys
import argparse

import data_loader  
from portfolio import Portfolio
from engine import ExecutionEngine
from strategies import MovingAverageCrossoverStrategy, MomentumStrategy

def parse_args(args):
    parser = argparse.ArgumentParser(description="Trading system")
    parser.add_argument('-d', "--csv_path", type=Path, default="data/market_data.csv")
    parser.add_argument('-q', "--quantity", type=int, default=10)
    parser.add_argument('-f', "--failure_rate", type=float, default=0.05)
    parser.add_argument('-c', "--cash", type=float, default=100000)

    return parser.parse_args(args)

def main(args):
    parsed_args = parse_args(args)
    csv_path = parsed_args.csv_path
    quantity = parsed_args.quantity
    failure_rate = parsed_args.failure_rate
    cash = parsed_args.cash
    # data_generator.generate_market_csv(csv_path)
    ticks = data_loader.load_market_data(csv_path)
    print(f"Loaded {len(ticks)} market data points.")
    
    strategies = [MovingAverageCrossoverStrategy(quantity=quantity), MomentumStrategy(quantity=quantity)]

    portfolio = Portfolio(cash=cash)
    engine = ExecutionEngine(strategies, portfolio, failure_rate)
    engine.process_ticks(ticks)

    # Get final prices for each symbol
    final_prices = {}
    for tick in reversed(ticks):
        if tick.symbol not in final_prices:
            final_prices[tick.symbol] = tick.price
    
    # Calculate total portfolio value
    holdings = portfolio.get_all_holdings()
    total_value = portfolio.get_total_value(final_prices)
    holdings_value = total_value - portfolio.cash
    
    print(f"\n{'='*50}")
    print(f"FINAL PORTFOLIO SUMMARY")
    print(f"{'='*50}")
    print(f"Initial capital:     ${cash:,.2f}")
    print(f"Final cash:          ${portfolio.cash:,.2f}")
    print(f"Holdings value:      ${holdings_value:,.2f}")
    print(f"Total portfolio:     ${total_value:,.2f}")
    print(f"P&L:                 ${total_value - cash:,.2f} ({((total_value - cash) / cash * 100):+.2f}%)")
    
    if holdings:
        print(f"\nCurrent Holdings:")
        for symbol, holding in holdings.items():
            current_price = final_prices.get(symbol, 0)
            position_value = holding["quantity"] * current_price
            print(f"  {symbol}: {holding['quantity']} shares @ ${current_price:.2f} = ${position_value:,.2f}")

if __name__ == "__main__":
    main(sys.argv[1:])
