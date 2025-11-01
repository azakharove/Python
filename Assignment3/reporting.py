from __future__ import annotations

import os
import re
import pstats
from typing import Iterable, Optional, Tuple
from datetime import datetime


# BASE_DIR = repo root (one level above this file's folder)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def _results_dir_for_size(data_size: str) -> str:
    return os.path.join(BASE_DIR, "Assignment3", f"Assignment_3_Results_{data_size}")

def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def get_prof_file_name(strategy_name: str, data_size: str) -> str:
    return os.path.join(
        _results_dir_for_size(data_size),
        f"{strategy_name}_cprofile.prof",
    )

def _readable_prof_path(strategy_name: str, data_size: str) -> str:
    return os.path.join(
        _results_dir_for_size(data_size),
        f"{strategy_name}_readable_prof.md",
    )

def prof_to_readable(strategy_name: str, data_size: str) -> str:
    """
    Convert a .prof file to a readable Markdown dump limited to top 10 cumulative funcs
    """
    prof_file = get_prof_file_name(strategy_name, data_size)
    out_dir = _results_dir_for_size(data_size)
    _ensure_dir(out_dir)

    output_file = _readable_prof_path(strategy_name, data_size)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Profiling Summary for {strategy_name} | {data_size} ticks\n\n")
        pstats.Stats(prof_file, stream=f).sort_stats("cumulative").print_stats(10)

    return output_file

def _parse_prof_readable_md(md_path: str) -> dict:
    """
    Parse a *_readable_prof.md file to extract:
      - function_calls (int)
      - total_seconds (float)
      - avg_ms_per_call (float)
    Returns {} if not found/missing.
    """
    if not os.path.exists(md_path):
        return {}

    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    m = re.search(
        r"(\d[\d,]*)\s+function\s+calls\s+in\s+([\d\.]+)\s+seconds",
        text,
        flags=re.IGNORECASE,
    )
    if not m:
        return {}

    calls = int(m.group(1).replace(",", ""))
    secs = float(m.group(2))
    avg_ms = (secs / calls) * 1000 if calls > 0 else None

    return {
        "function_calls": calls,
        "total_seconds": secs,
        "avg_ms_per_call": avg_ms,
    }

def prof_runtime_summary(
    strategy_names: Iterable[str],
    data_sizes: Iterable[str],
    summary_filename: str = "profiling_runtime_summary.md",
    regenerate_readables: bool = True,
) -> str:
    """
    For every (strategy, data_size):
      - (Optionally) regenerate the readable cProfile MD via prof_to_readable
      - Parse runtime metrics from *_readable_prof.md
      - Write a Markdown table comparing the metrics

    Returns: absolute path to the summary MD file.
    """
    rows: list[Tuple[str, str, Optional[int], Optional[float], Optional[float], str]] = []

    for s in strategy_names:
        for d in data_sizes:
            if regenerate_readables:
                try:
                    prof_to_readable(s, d)
                except FileNotFoundError:
                    pass

            md_path = _readable_prof_path(s, d)
            metrics = _parse_prof_readable_md(md_path)

            calls = metrics.get("function_calls")
            secs = metrics.get("total_seconds")
            avg_ms = metrics.get("avg_ms_per_call")

            rows.append((s, d, calls, secs, avg_ms))

    out_dir = os.path.join(BASE_DIR, "Assignment3")
    _ensure_dir(out_dir)
    out_path = os.path.join(out_dir, summary_filename)

    # Write the table
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Runtime Profiling Summary\n\n")
        f.write(
            "| Strategy | Data Size | Function Calls | Total Time (s) | Avg Time / Call (ms) |\n"
            "|----------|-----------|----------------|----------------|---------------------|\n"
        )
        for s, d, calls, secs, avg_ms in rows:
            calls_str = f"{calls:,}" if isinstance(calls, int) else ""
            secs_str = f"{secs:.6f}" if isinstance(secs, (int, float)) else ""
            avg_ms_str = f"{avg_ms:.3f}" if isinstance(avg_ms, (int, float)) else ""
            f.write(f"| {s} | {d} | {calls_str} | {secs_str} | {avg_ms_str} |\n")

        f.write(
            "\n> Notes: Parsed from each `*_readable_prof.md` line matching "
            "`<N> function calls in <S> seconds`. Average time per call is `S / N * 1000`.\n"
        )

    return out_path

def write_report(
    strategies: list[str],
    data_sizes: list[str],
    report_filename: str = "complexity_report.md",
    regenerate_readables: bool = True,
) -> str:
    """
    Builds a single Markdown report that embeds the runtime summary table.
    Returns the absolute path to the report.
    """
    runtime_table_path = prof_runtime_summary(
        strategies, data_sizes, regenerate_readables=regenerate_readables
    )

    with open(runtime_table_path, "r") as f:
        runtime_table_md = f.read()

    report_dir = os.path.join(BASE_DIR, "Assignment3")
    _ensure_dir(report_dir)
    report_path = os.path.join(report_dir, report_filename)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(report_path, "w") as f:
        f.write("# Assignment 3 – Profiling Report\n\n")
        f.write(f"_Generated: {timestamp}_\n\n")
        f.write("## 1) Runtime Metrics\n\n")
        f.write(runtime_table_md)
        f.write("\n")

    return report_path


if __name__ == "__main__":
    strategy_names = ["NaiveMovingAverageStrategy", "OptimizedMovingAverageStrategy"]
    data_sizes = ["1k", "10k", "100k"]

    report_path = write_report(strategy_names, data_sizes)
    print(f"Report written to:\n{report_path}")
