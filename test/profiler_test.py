# tests/test_profiler_outputs.py
from __future__ import annotations

import os
from pathlib import Path
import pstats

from Assignment3.profiler import StrategyProfiler
from Assignment3.strategies import NaiveMovingAverageStrategy
from trading_lib.models import RecordingInterval
from trading_lib.data_generator import generate_market_csv


def _run_and_assert_outputs(out_dir: Path):

    out_dir.mkdir(parents=True, exist_ok=True)

    data_path = out_dir / "market_data_test.csv"
    generate_market_csv(
        symbol="AAPL",
        start_price=150,
        filename=str(data_path),
        num_ticks=1_000,
    )

    StrategyProfiler(output_path=str(out_dir)).profile_strategies(
        strategies=[NaiveMovingAverageStrategy(quantity=10)],
        cash=100_000,
        failure_rate=0.0,
        interval=RecordingInterval("1s"),
        price_path=data_path,
    )

    strategy_name = "NaiveMovingAverageStrategy"
    prof_files = list(out_dir.rglob(f"{strategy_name}_cprofile.prof"))
    mem_files  = list(out_dir.rglob(f"{strategy_name}_memory.md"))
    perf_files = list(out_dir.rglob(f"{strategy_name}_performance.md"))

    # existence
    assert prof_files, "cProfile file was not written"
    assert mem_files,  "Memory report (.md) was not written"
    assert perf_files, "Runtime/Performance report (.md) was not written"

    # non-empty
    for f in prof_files + mem_files + perf_files:
        assert os.path.getsize(f) > 0, f"{f.name} is empty"

    # readable .prof
    ps = pstats.Stats(str(prof_files[0]))
    assert len(ps.stats) > 0, "cProfile stats are empty/unreadable"


def test_profiler_writes_expected_artifacts(tmp_path):
    """Pytest entrypoint: uses tmp_path for hermetic outputs."""
    _run_and_assert_outputs(tmp_path)


if __name__ == "__main__":
    out_dir = Path("./test_outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    _run_and_assert_outputs(out_dir)
