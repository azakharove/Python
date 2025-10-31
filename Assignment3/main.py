from pathlib import Path
import sys, argparse
import pandas as pd

from trading_lib.models import RecordingInterval
from strategies import NaiveMovingAverageStrategy, OptimizedMovingAverageStrategy

from profiler import ProfilerStrategyComparator   # <— use this
import reporting                                  # <— your markdown/plots module

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA = PROJECT_ROOT / "data"

DATA_1K   = DATA / "market_data_1k.csv"
DATA_10K  = DATA / "market_data_10k.csv"
DATA_100K = DATA / "market_data_100k.csv"

def parse_args(argv):
    p = argparse.ArgumentParser()
    p.add_argument("-q","--quantity", type=int, default=10)
    p.add_argument("-f","--failure_rate", type=float, default=0.05)
    p.add_argument("-c","--cash", type=float, default=100000)
    p.add_argument("-i","--interval", type=str, default="1s",
                   choices=[e.value for e in RecordingInterval])
    return p.parse_args(argv)

def main(argv):
    args = parse_args(argv)
    interval = RecordingInterval(args.interval)

    strategies = [
        NaiveMovingAverageStrategy(quantity=args.quantity),
        OptimizedMovingAverageStrategy(quantity=args.quantity),
    ]

    runs = []
    cprof_maps = []

    for label, path in [("1k", DATA_1K), ("10k", DATA_10K), ("100k", DATA_100K)]:
        if not path.exists():
            print(f"[skipping] {label}: {path} not found")
            continue

        comp = ProfilerStrategyComparator(output_path=f"Assignment_3_Results_{label}", dataset_label=label)
        df, cmap = comp.compare_and_profile(
            strategies=strategies,
            cash=args.cash,
            failure_rate=args.failure_rate,
            interval=interval,
            price_path=path
        )
        runs.append(df); cprof_maps.append(cmap)

    if not runs:
        print("No datasets profiled.")
        return

    df_all = pd.concat(runs, ignore_index=True)
    # Flatten the cProfile maps
    all_cprof = {}
    for m in cprof_maps:
        all_cprof.update(m)

    out_root = Path("Assignment_3_Results_Scaling")
    out_root.mkdir(parents=True, exist_ok=True)
    report_path = reporting.generate_complexity_report(df_all, all_cprof, out_root)
    print(f"Complexity report written to: {report_path}")

if __name__ == "__main__":
    main(sys.argv[1:])
