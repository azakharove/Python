from pathlib import Path
import sys
import argparse
import os

from trading_lib.models import RecordingInterval
from trading_lib.StrategyComparator import StrategyComparator
from strategies import  NaiveMovingAverageStrategy, OptimizedMovingAverageStrategy
import profiler
import reporting

# Local Assignment3 modules
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

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # go up one level
DATA_PATH_1k = os.path.join(BASE_DIR, "data", "market_data_1k.csv")
DATA_PATH_10k = os.path.join(BASE_DIR, "data", "market_data_10k.csv")
DATA_PATH_100k = os.path.join(BASE_DIR, "data", "market_data_100k.csv")

def main(args):
    parsed_args = parse_args(args)
    quantity = parsed_args.quantity
    
    # data_generator.generate_market_csv(DATA_PATH_1k)
    # data_generator.generate_market_csv(DATA_PATH_10k)
    # data_generator.generate_market_csv(DATA_PATH_100k)

    strategies = [NaiveMovingAverageStrategy(quantity=quantity), OptimizedMovingAverageStrategy(quantity=quantity)]
    
    StrategyComparator(output_path = "Assignment_3_Results_1k").compare_strategies(
        strategies, 
        parsed_args.cash, 
        parsed_args.failure_rate, 
        RecordingInterval(parsed_args.interval), 
        Path(DATA_PATH_1k))
    
    StrategyComparator(output_path = "Assignment_3_Results_10k").compare_strategies(
        strategies, 
        parsed_args.cash, 
        parsed_args.failure_rate, 
        RecordingInterval(parsed_args.interval), 
        Path(DATA_PATH_10k))
    
    StrategyComparator(output_path = "Assignment_3_Results_100k").compare_strategies(
        strategies,
        parsed_args.cash,
        parsed_args.failure_rate,
        RecordingInterval(parsed_args.interval),
        Path(DATA_PATH_100k))
    

if __name__ == "__main__":
    main(sys.argv[1:])