from pathlib import Path
import sys
import argparse
import os

from trading_lib.models import RecordingInterval
from trading_lib.StrategyComparator import StrategyComparator
from profiler import StrategyProfiler
from strategies import  NaiveMovingAverageStrategy, OptimizedMovingAverageStrategy
from trading_lib.data_generator import generate_market_csv
import reporting

# Local Assignment3 modules
sys.path.insert(0, str(Path(__file__).parent))

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def parse_args(args):
    parser = argparse.ArgumentParser(description = "Trading system")
    parser.add_argument('-d', "--csv_path", type = Path, default = "data/market_data.csv")
    parser.add_argument('-q', "--quantity", type = int, default = 10)
    parser.add_argument('-f', "--failure_rate", type = float, default = 0.05)
    parser.add_argument('-c', "--cash", type = float, default = 100000)
    parser.add_argument('-i', "--interval", type = str, default = "1s",
                        choices = [e.value for e in RecordingInterval],
                        help="Portfolio recording interval (tick, 1s, 1m, 1h, 1d, 1mo)")
    parser.add_argument('-g', "--generate", type = bool, default = False, 
                        help = "Generate test data for 1k, 10k, 100k ticks before executing strategies")

    return parser.parse_args(args)

def data_path_for_size(size = str) -> Path:
    return os.path.join(BASE_DIR, "data", "market_data_" + size + ".csv")

def main(args):
    parsed_args = parse_args(args)
    quantity = parsed_args.quantity
    generate = parsed_args.generate

    data_sizes = {"1k": 1000, "10k": 10000, "100k":100000}

    if generate:
        for key, value in data_sizes.items():
            generate_market_csv(symbol = "AAPL", 
                                start_price = 150, 
                                filename = data_path_for_size(key),
                                num_ticks = value)
            
    strategies = [NaiveMovingAverageStrategy(quantity=quantity), OptimizedMovingAverageStrategy(quantity=quantity)]

    # for data_size in data_sizes:
    #    StrategyComparator(output_path = "Assignment_3_Results_" + data_size).compare_strategies(
    #         strategies, 
    #         parsed_args.cash, 
    #         parsed_args.failure_rate, 
    #         RecordingInterval(parsed_args.interval), 
    #         Path(data_path_for_size(data_size)))  

    for data_size in data_sizes:
       StrategyProfiler(output_path = "Assignment_3_Results_" + data_size).profile_strategies(
            strategies, 
            parsed_args.cash, 
            parsed_args.failure_rate, 
            RecordingInterval(parsed_args.interval), 
            Path(data_path_for_size(data_size)))  

if __name__ == "__main__":
    main(sys.argv[1:])