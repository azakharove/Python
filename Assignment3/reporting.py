from __future__ import annotations

import os
import re
import pstats
import matplotlib.pyplot as plt
import io
import base64
from typing import Iterable, Optional, Tuple
from datetime import datetime


# BASE_DIR = repo root (one level above this file's folder)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def _results_dir_for_size(data_size: str) -> str:
    # Check both possible locations: root level and Assignment3 subdirectory
    root_path = os.path.join(BASE_DIR, f"Assignment_3_Results_{data_size}")
    sub_path = os.path.join(BASE_DIR, "Assignment3", f"Assignment_3_Results_{data_size}")
    
    if os.path.exists(root_path):
        return root_path
    else:
        return sub_path

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

def _memory_path(strategy_name: str, data_size: str) -> str:
    return os.path.join(
        _results_dir_for_size(data_size),
        f"{strategy_name}_memory.md",
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

def _parse_memory_md(md_path: str) -> Optional[float]:
    """
    Parse a *_memory.md file to extract max memory usage in MiB.
    Returns None if not found/missing.
    """
    if not os.path.exists(md_path):
        return None

    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    m = re.search(r"([\d\.]+)\s*MiB", text, flags=re.IGNORECASE)
    if not m:
        return None

    return float(m.group(1))

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
    rows: list[Tuple[str, str, Optional[int], Optional[float], Optional[float]]] = []

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

def prof_memory_summary(
    strategy_names: Iterable[str],
    data_sizes: Iterable[str],
) -> str:
    """
    For every (strategy, data_size):
      - Parse memory metrics from *_memory.md
      - Return a Markdown table as a string

    Returns: Markdown table string.
    """
    rows: list[Tuple[str, str, Optional[float]]] = []

    for s in strategy_names:
        for d in data_sizes:
            mem_path = _memory_path(s, d)
            mem_mib = _parse_memory_md(mem_path)
            rows.append((s, d, mem_mib))

    lines = []
    lines.append("# Memory Profiling Summary\n\n")
    lines.append(
        "| Strategy | Data Size | Max Memory Usage (MiB) |\n"
        "|----------|-----------|----------------------|\n"
    )
    for s, d, mem_mib in rows:
        mem_str = f"{mem_mib:.2f}" if isinstance(mem_mib, (int, float)) else ""
        lines.append(f"| {s} | {d} | {mem_str} |\n")

    lines.append(
        "\n> Notes: Parsed from each `*_memory.md` file showing peak memory usage.\n"
    )

    return "".join(lines)

def generate_plots(
    strategy_names: Iterable[str],
    data_sizes: Iterable[str],
    out_dir: Optional[str] = None
) -> Tuple[str, str]:
    """
    Generate runtime and memory usage plots comparing strategies as base64-encoded images.
    Returns: tuple of (runtime_plot_base64_md, memory_plot_base64_md)
    """
    # Collect data
    runtime_data = []
    memory_data = []
    
    for s in strategy_names:
        for d in data_sizes:
            # Runtime data
            md_path = _readable_prof_path(s, d)
            metrics = _parse_prof_readable_md(md_path)
            secs = metrics.get("total_seconds")
            
            # Memory data
            mem_path = _memory_path(s, d)
            mem_mib = _parse_memory_md(mem_path)
            
            if secs is not None:
                runtime_data.append((s, d, secs))
            if mem_mib is not None:
                memory_data.append((s, d, mem_mib))
    
    # Prepare for plotting
    data_size_list = list(data_sizes)
    
    # Runtime plot
    runtime_fig, runtime_ax = plt.subplots(figsize=(10, 6))
    for strategy in strategy_names:
        times = []
        for d in data_size_list:
            # Find data for this strategy/data_size combination
            time_val = None
            for s, d_size, secs in runtime_data:
                if s == strategy and d_size == d:
                    time_val = secs
                    break
            times.append(time_val)
        
        if any(t is not None for t in times):
            runtime_ax.plot(data_size_list, times, marker='o', label=strategy)
    
    runtime_ax.set_xlabel('Data Size')
    runtime_ax.set_ylabel('Total Time (s)')
    runtime_ax.set_title('Runtime Performance Comparison')
    runtime_ax.legend()
    runtime_ax.grid(True, alpha=0.3)
    
    # Convert to base64
    # buf = io.BytesIO()
    # runtime_fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    # buf.seek(0)
    # runtime_base64 = base64.b64encode(buf.read()).decode('utf-8')
    # plt.close(runtime_fig)
    
    # Memory plot
    memory_fig, memory_ax = plt.subplots(figsize=(10, 6))
    for strategy in strategy_names:
        memories = []
        for d in data_size_list:
            # Find data for this strategy/data_size combination
            mem_val = None
            for s, d_size, mem in memory_data:
                if s == strategy and d_size == d:
                    mem_val = mem
                    break
            memories.append(mem_val)
        
        if any(m is not None for m in memories):
            memory_ax.plot(data_size_list, memories, marker='o', label=strategy)
    
    memory_ax.set_xlabel('Data Size')
    memory_ax.set_ylabel('Max Memory Usage (MiB)')
    memory_ax.set_title('Memory Usage Comparison')
    memory_ax.legend()
    memory_ax.grid(True, alpha=0.3)
    
    # # Convert to base64
    # buf = io.BytesIO()
    # memory_fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    # buf.seek(0)
    # memory_base64 = base64.b64encode(buf.read()).decode('utf-8')
    # plt.close(memory_fig)

    if out_dir is None:
        out_dir = os.path.join(BASE_DIR, "Assignment3", "plots")
    _ensure_dir(out_dir)
    
    runtime_path = os.path.join(out_dir, "runtime_comparison.png")
    memory_path = os.path.join(out_dir, "memory_comparison.png")
    runtime_fig.savefig(runtime_path, format='png', dpi=150, bbox_inches='tight')
    memory_fig.savefig(memory_path, format='png', dpi=150, bbox_inches='tight')
    plt.close(runtime_fig)
    plt.close(memory_fig)

    rel_runtime = os.path.join("plots", "runtime_comparison.png")
    rel_memory = os.path.join("plots", "memory_comparison.png")
   
    return rel_runtime, rel_memory

def memory_metrics(strategies: list[str], data_sizes: list[str]) -> str:
    memory_metrics = []
    for s in strategies:
        for d in data_sizes:
            mem_path = _memory_path(s, d)
            mem_mib = _parse_memory_md(mem_path)
            if mem_mib is not None:
                memory_metrics.append((s, d, mem_mib))
    return memory_metrics

def time_metrics(strategies: list[str], data_sizes: list[str]) -> str:
    time_metrics = []
    for s in strategies:
        for d in data_sizes:
            md_path = _readable_prof_path(s, d)
            metrics = _parse_prof_readable_md(md_path)
            secs = metrics.get("total_seconds")
            if secs is not None:
                time_metrics.append((s, d, secs))
    return time_metrics

def total_for(strategy: str, metrics: list[tuple[str, str, float]]) -> float:
    return sum(v for s, _, v in metrics if s.lower() == strategy.lower())

def write_narrative(
        memory_metrics: list[tuple[str, str, float]],
        time_metrics: list[tuple[str, str, float]],
    ) -> str:
    """
    Generate a short Markdown narrative comparing optimized vs naive strategies.
    """
    if not memory_metrics or not time_metrics:
        return "## Interpretation\n- No profiling data found."

    opt_name = next((s for s, _, _ in memory_metrics + time_metrics if "opt" in s.lower()), "Optimized")
    naive_name = next((s for s, _, _ in memory_metrics + time_metrics if "naiv" in s.lower()), "Naive")

    total_time_opt = total_for(opt_name, time_metrics)
    total_time_naive = total_for(naive_name, time_metrics)
    total_mem_opt = total_for(opt_name, memory_metrics)
    total_mem_naive = total_for(naive_name, memory_metrics)

    faster = total_time_opt < total_time_naive
    lighter = total_mem_opt < total_mem_naive

    narrative = "## Interpretation\n"

    if faster and lighter:
        narrative += "- **Excellent**: Optimization improved both runtime and memory efficiency.\n"
    elif faster and not lighter:
        narrative += "- **Trade-off**: Optimization runs faster but uses more memory.\n"
    elif not faster and lighter:
        narrative += "- **Trade-off**: Optimization reduces memory but increases runtime.\n"
    else:
        narrative += "- **Neutral**: No significant performance improvement observed.\n"

    # Check scalability (improves more with larger sizes)
    size_map = {"1k": 1_000, "10k": 10_000, "100k": 100_000, "1m": 1_000_000}
    time_opt_by_size = sorted(
        [(size_map.get(d.lower(), 0), v) for s, d, v in time_metrics if s == opt_name]
    )
    time_naive_by_size = sorted(
        [(size_map.get(d.lower(), 0), v) for s, d, v in time_metrics if s == naive_name]
    )
    if len(time_opt_by_size) >= 2 and len(time_naive_by_size) >= 2:
        opt_gain = (time_naive_by_size[-1][1] - time_opt_by_size[-1][1]) - (
            time_naive_by_size[0][1] - time_opt_by_size[0][1]
        )
        if opt_gain > 0:
            narrative += "- **Scalability**: Optimized performance improves as data size grows.\n"

    return narrative

    
def write_report(
    strategies: list[str],
    data_sizes: list[str] = ["1k", "10k", "100k"],
    report_filename: str = "complexity_report.md",
    regenerate_readables: bool = True,
    generate_plots_flag: bool = True,
) -> str:
    """
    Builds a single Markdown report that embeds the runtime and memory summary tables.
    Optionally generates comparison plots.
    Returns the absolute path to the report.
    """
    runtime_table_path = prof_runtime_summary(
        strategies, data_sizes, regenerate_readables=regenerate_readables
    )
    memory_table_md = prof_memory_summary(strategies, data_sizes)

    with open(runtime_table_path, "r") as f:
        runtime_table_md = f.read()

    report_dir = os.path.join(BASE_DIR, "Assignment3")
    _ensure_dir(report_dir)
    report_path = os.path.join(report_dir, report_filename)

    # Generate plots if requested
    runtime_plot_md = ""
    memory_plot_md = ""
    if generate_plots_flag:
        try:
            # pass the Assignment3/plots dir so paths are consistent
            plots_dir = os.path.join(BASE_DIR, "Assignment3", "plots")
            runtime_rel, memory_rel = generate_plots(strategies, data_sizes, out_dir=plots_dir)
            runtime_plot_md = f"\n![Runtime Comparison]({runtime_rel})\n"
            memory_plot_md = f"\n![Memory Comparison]({memory_rel})\n"
        except Exception as e:
            print(f"Warning: Failed to generate plots: {e}")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    memory_stats = memory_metrics(strategies, data_sizes)
    time_stats = time_metrics(strategies, data_sizes)

    narrative = write_narrative(
        memory_metrics=memory_stats,
        time_metrics=time_stats
    )   

    with open(report_path, "w") as f:
        f.write("# Assignment 3 – Profiling Report\n\n")
        f.write(f"_Generated: {timestamp}_\n\n")
        f.write("## 1) Runtime Metrics\n\n")
        f.write(runtime_table_md)
        if runtime_plot_md:
            f.write(runtime_plot_md)
        f.write("\n")
        f.write("## 2) Memory Usage\n\n")
        f.write(memory_table_md)
        if memory_plot_md:
            f.write(memory_plot_md)
        f.write("\n")
        f.write("## 3) Performance Interpretation\n\n")
        f.write(narrative)
        f.write("\n")

    return report_path


if __name__ == "__main__":
    strategy_names = ["NaiveMovingAverageStrategy", "OptimizedMovingAverageStrategy"]
    data_sizes = ["1k", "10k", "100k"]

    report_path = write_report(strategy_names, data_sizes)
    print(f"Report written to:\n{report_path}")
