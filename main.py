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

    print(f"Final portfolio cash: {portfolio.cash}")

if __name__ == "__main__":
    main(sys.argv[1:])
