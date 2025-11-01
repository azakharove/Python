from __future__ import annotations
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
import pstats
import sys
import os

def get_prof_file_name(strategy_name: str, data_size:str) -> str:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(BASE_DIR, 
                        "Assignment3",
                        "Assignment_3_Results_" + data_size, 
                        strategy_name + "_cprofile.prof")

def prof_to_readable_one(strategy_name: str, data_size: str) -> str:
    prof_file = get_prof_file_name(strategy_name, data_size)
    with open(strategy_name + data_size + "_prof_summary.md", "w") as f:
        ps = pstats.Stats(prof_file, stream=f)
        f.write(f"# Profiling Summary for {strategy_name} with {data_size} ticks\n\n")
        ps.sort_stats('cumulative').print_stats(10)
        ps.print_stats()
    return strategy_name + data_size + "_prof_summary.md"

if __name__ == "__main__":
    strategy_names = ["NaiveMovingAverageStrategy", "OptimizedMovingAverageStrategy"]
    data_sizes = ["1k", "10k", "100k"]
    prof_to_readable_one(strategy_names[0], data_sizes[0])


