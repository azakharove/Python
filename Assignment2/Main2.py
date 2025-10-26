from pathlib import Path
import sys
import argparse

from trading_lib.models import RecordingInterval
from trading_lib.StrategyComparator import StrategyComparator
from trading_lib.strategies import MovingAverageCrossoverStrategy, MomentumStrategy
from BenchmarkStrategy import BenchmarkStrategy

# Local Assignment1 modules
sys.path.insert(0, str(Path(__file__).parent))

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
    quantity = parsed_args.quantity
    
    # data_generator.generate_market_csv(csv_path)

    strategies = [MovingAverageCrossoverStrategy(quantity=quantity), BenchmarkStrategy()]

    StrategyComparator(path = "Assignment_2_Results").compare_strategies(
        strategies, 
        parsed_args.cash, 
        parsed_args.failure_rate, 
        RecordingInterval(parsed_args.interval), 
        parsed_args.csv_path)

if __name__ == "__main__":
    main(sys.argv[1:])