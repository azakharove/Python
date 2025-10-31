from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple
import math

import pandas as pd
import matplotlib.pyplot as plt

def _fit_loglog_slope(ns, ys) -> float | None:
    """Return slope b of log(y) ~ a + b log(n), or None if invalid."""
    ns = list(ns); ys = list(ys)
    if len(ns) < 2 or len(ys) < 2:
        return None
    xs, ls = [], []
    for n, y in zip(ns, ys):
        if n is None or n <= 0 or y is None or y <= 0:
            return None
        xs.append(math.log(n)); ls.append(math.log(y))
    xbar, ybar = sum(xs)/len(xs), sum(ls)/len(ls)
    num = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ls))
    den = sum((x - xbar) ** 2 for x in xs)
    return None if den == 0 else num / den


def _cx_label(slope: float | None) -> str:
    if slope is None: return "n/a"
    if slope < 0.3:  return "≈ O(1)–O(log n)"
    if slope < 0.8:  return "≈ sub-linear"
    if slope < 1.2:  return "≈ O(n)"
    if slope < 1.7:  return "≈ O(n^1.5)"
    if slope < 2.3:  return "≈ O(n^2)"
    return f"≈ O(n^{slope:.1f})"


def _plot_runtime(df: pd.DataFrame, out_root: Path) -> Path:
    """Plot total_time_s vs n_ticks per strategy."""
    out = out_root / "runtime_scaling.png"
    plt.figure()
    for sname, sdf in df.groupby("strategy_name"):
        sdf = sdf.sort_values("n_ticks")
        plt.plot(sdf["n_ticks"], sdf["total_time_s"], marker="o", label=sname)
    plt.xlabel("Input size (# ticks)")
    plt.ylabel("Total execution time (s)")
    plt.title("Runtime vs Input Size")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    return out


def _plot_memory(df: pd.DataFrame, out_root: Path) -> Path | None:
    """Plot peak_mem_mib vs n_ticks per strategy (skip if empty)."""
    out = out_root / "memory_scaling.png"
    dff = df.dropna(subset=["peak_mem_mib"])
    if dff.empty:
        return None
    plt.figure()
    for sname, sdf in dff.groupby("strategy_name"):
        sdf = sdf.sort_values("n_ticks")
        plt.plot(sdf["n_ticks"], sdf["peak_mem_mib"], marker="o", label=sname)
    plt.xlabel("Input size (# ticks)")
    plt.ylabel("Peak memory (MiB)")
    plt.title("Peak Memory vs Input Size")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    return out


def _narrative(df: pd.DataFrame, time_cx: dict, mem_cx: dict) -> str:
    """Short comparison narrative driven by measured data & annotations."""
    lines = ["We measured total runtime (timeit), peak memory (memory_profiler), and CPU hotspots (cProfile)."]
    for sname, sdf in df.groupby("strategy_name"):
        sdf = sdf.sort_values("n_ticks")
        small, large = sdf.iloc[0], sdf.iloc[-1]
        t_ratio = (large["total_time_s"] / small["total_time_s"]) if small["total_time_s"] > 0 else float("inf")
        if pd.notna(large["peak_mem_mib"]) and pd.notna(small["peak_mem_mib"]) and small["peak_mem_mib"] > 0:
            m_ratio = large["peak_mem_mib"] / small["peak_mem_mib"]
            mem_note = f" Peak memory grew by ~×{m_ratio:.1f} ({mem_cx.get(sname,'n/a')})."
        else:
            mem_note = " Peak memory annotation unavailable."
        lines.append(f"- **{sname}**: runtime grew by ~×{t_ratio:.1f} (annotated {time_cx.get(sname,'n/a')}).{mem_note}")

    if df["strategy_name"].nunique() >= 2 and not df.empty:
        largest_n = df["n_ticks"].max()
        sub = df[df["n_ticks"] == largest_n].sort_values("total_time_s")
        if len(sub) >= 2:
            best = sub.iloc[0]
            lines.append(f"\nAt n={largest_n}, **{best['strategy_name']}** is faster ({best['total_time_s']:.3f}s).")
    return "\n".join(lines)

def generate_complexity_report(
    df: pd.DataFrame,
    cprofile_map: Dict[Tuple[str, str, int], str],
    out_root: Path | str,
    cprofile_snippets_per_strategy: int = 2,
) -> Path:
    """
    Create markdown + plots for Section 4.
    Returns the path to complexity_report.md.
    """
    out_root = Path(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    runtime_png = _plot_runtime(df, out_root)
    memory_png = _plot_memory(df, out_root) 

    # complexity annotations
    time_cx, mem_cx = {}, {}
    for sname, sdf in df.groupby("strategy_name"):
        sdf = sdf.sort_values("n_ticks")
        time_cx[sname] = _cx_label(_fit_loglog_slope(sdf["n_ticks"], sdf["total_time_s"]))
        if any(pd.isna(sdf["peak_mem_mib"])):
            mem_cx[sname] = "n/a"
        else:
            mem_cx[sname] = _cx_label(_fit_loglog_slope(sdf["n_ticks"], sdf["peak_mem_mib"]))

    # narrative
    narrative = _narrative(df, time_cx, mem_cx)

    # tables
    runtime_tbl = df.pivot_table(index="n_ticks", columns="strategy_name", values="total_time_s", aggfunc="first")
    mem_tbl = df.pivot_table(index="n_ticks", columns="strategy_name", values="peak_mem_mib", aggfunc="first")

    # select cProfile snippets: smallest & largest n per strategy (up to N)
    selected = []
    for sname, sdf in df.groupby("strategy_name"):
        sdf = sdf.sort_values("n_ticks")
        picks = [sdf.iloc[0], sdf.iloc[-1]] if len(sdf) > 1 else [sdf.iloc[0]]
        for row in picks[:max(1, cprofile_snippets_per_strategy)]:
            key = (row["strategy_name"], row["dataset_label"], int(row["n_ticks"]))
            selected.append((row["strategy_name"], row["dataset_label"], int(row["n_ticks"]), cprofile_map.get(key, "")))

    # write markdown
    report_path = out_root / "complexity_report.md"
    with report_path.open("w", encoding="utf-8") as f:
        f.write("# Complexity Report (Section 4)\n\n")
        f.write("Measured **total execution time** (`timeit`), **CPU hotspots** (`cProfile`), and "
                "**peak memory** (`memory_profiler`) for each strategy at each input size.\n\n")

        f.write("## Tables of Runtime and Memory Metrics\n\n")
        f.write("### Total Execution Time (seconds)\n\n")
        f.write(runtime_tbl.to_markdown() + "\n\n")
        f.write("### Peak Memory (MiB)\n\n")
        f.write(mem_tbl.to_markdown() + "\n\n")

        f.write("## Complexity Annotations\n\n")
        for s in sorted(df["strategy_name"].unique()):
            f.write(f"- **{s}** — Time: {time_cx.get(s,'n/a')}; Memory: {mem_cx.get(s,'n/a')}\n")
        f.write("\n")

        f.write("## Plots of Scaling Behavior\n\n")
        f.write(f"![Runtime vs Input Size]({runtime_png.name})\n\n")
        if memory_png:
            f.write(f"![Peak Memory vs Input Size]({memory_png.name})\n\n")
        else:
            f.write("_Peak memory plot omitted (no memory data available)._ \n\n")

        f.write("## Narrative Comparing Strategies and Optimization Impact\n\n")
        f.write(narrative + "\n\n")

        f.write("## Selected cProfile Hotspots (smallest & largest n per strategy)\n\n")
        for sname, dlabel, n, block in selected:
            f.write(f"### {sname} on {dlabel} (n={n})\n\n```text\n{block}\n```\n\n")

    return report_path
