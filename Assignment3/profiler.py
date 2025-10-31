from __future__ import annotations

import io
import os
import csv
import cProfile
import pstats
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from timeit import default_timer

from trading_lib.strategy import Strategy
from trading_lib.models import RecordingInterval, MarketDataPoint
from trading_lib.data_loader import load_market_data, load_market_data_yf
from trading_lib.engine import ExecutionEngine
from trading_lib.portfolio import Portfolio
from trading_lib.reporting import generate_performance_report, calc_performance_metrics

try:
    from memory_profiler import memory_usage
    _HAS_MEMPROF = True
except Exception:
    _HAS_MEMPROF = False


@dataclass
class MeasureRow:
    strategy_name: str
    dataset_label: str
    n_ticks: int
    total_time_s: float
    peak_mem_mib: float | None
    cprofile_top: str


def _cprofile_top_text(pr: cProfile.Profile, sortby: str = "cumtime", lines: int = 20) -> str:
    """Format the top lines from cProfile stats."""
    buf = io.StringIO()
    pstats.Stats(pr, stream=buf).strip_dirs().sort_stats(sortby).print_stats(lines)
    return buf.getvalue().rstrip()

class ProfilerStrategyComparator:
    """
    A light wrapper that mirrors your StrategyComparator behavior, but measures it.
    NOTE: We do NOT modify your StrategyComparator; we duplicate the small bits
    needed to call the exact same engine code and persist the same artifacts.
    """

    def __init__(self, output_path: str | Path = "", dataset_label: str = ""):
        self.output_path = str(output_path) if output_path else ""
        self.dataset_label = dataset_label or ""
        if self.output_path:
            Path(self.output_path).mkdir(parents=True, exist_ok=True)

    def _load_ticks(self, price_path: str | Path) -> List[MarketDataPoint]:
        price_path = Path(price_path)
        if price_path.is_file():
            return load_market_data(price_path)
        elif price_path.is_dir():
            return load_market_data_yf(price_path)
        raise ValueError(f"Invalid price path: {price_path}")

    def _infer_dataset_label(self, price_path: Path) -> str:
        if self.dataset_label:
            return self.dataset_label
        name = price_path.name
        return name.rsplit(".", 1)[0] if "." in name else name

    def _run_engine_once(
        self,
        strategy: Strategy,
        cash: float,
        failure_rate: float,
        interval: RecordingInterval,
        ticks: List[MarketDataPoint],
    ) -> tuple[Portfolio, dict, list[tuple[datetime, float]], dict[str, float]]:
        portfolio = Portfolio(cash=cash)
        engine = ExecutionEngine(strategy, portfolio, failure_rate, recording_interval=interval)
        engine.process_ticks(ticks)

        final_ts = max(t.timestamp for t in ticks)
        engine.record_final_state(final_ts)

        current_prices = engine.get_current_prices()
        periodic_returns = engine.get_portfolio_history()
        metrics = calc_performance_metrics(portfolio, cash, ticks, current_prices, periodic_returns)
        return portfolio, metrics, periodic_returns, current_prices

    def _print_portfolio_summary(self, portfolio: Portfolio, metrics: dict, current_prices: dict[str, float]):
        holdings = portfolio.get_all_holdings()
        holdings_value = metrics['final_value'] - portfolio.get_cash()

        print(f"\n{'='*60}")
        print("FINAL PORTFOLIO SUMMARY")
        print(f"{'='*60}")
        print(f"Initial capital:     ${metrics['starting_value']:,.2f}")
        print(f"Final cash:          ${portfolio.get_cash():,.2f}")
        print(f"Holdings value:      ${holdings_value:,.2f}")
        print(f"Total portfolio:     ${metrics['final_value']:,.2f}")
        print(f"P&L:                 ${metrics['pnl']:,.2f} ({metrics['total_return']:+.2f}%)")
        print(f"\n{'='*60}")
        print("PERFORMANCE METRICS")
        print(f"{'='*60}")
        print(f"Sharpe Ratio:        {metrics['sharpe_ratio']:.2f}")
        print(f"Max Drawdown:        {metrics['max_drawdown']:.2f}%")

        if holdings:
            print(f"\n{'='*60}")
            print("CURRENT HOLDINGS")
            print(f"{'='*60}")
            for symbol, holding in holdings.items():
                price = current_prices.get(symbol, 0)
                position_value = holding["quantity"] * price
                print(f"  {symbol}: {holding['quantity']} shares @ ${price:.2f} = ${position_value:,.2f}")

    def _persist_performance(self, strategy_name: str, metrics: dict, periodic_returns: list[tuple[datetime, float]]):
        out_file = f"{strategy_name}_performance.md"
        if self.output_path:
            out_file = str(Path(self.output_path) / out_file)
        generate_performance_report(metrics, periodic_returns, out_file)

    def _write_portfolio_history(self, portfolio_history: list[tuple[datetime, float, float]], strategy_name: str):
        out_file = f"{strategy_name}_portfolio_history.csv"
        if self.output_path:
            out_file = str(Path(self.output_path) / out_file)

        with open(out_file, "w", newline="") as csvfile: 
            writer = csv.writer(csvfile)
            writer.writerow(["Timestamp", "Cash", "Holdings"])
            writer.writerows(portfolio_history)

    def compare_and_profile(
        self,
        strategies: list[Strategy],
        cash: float,
        failure_rate: float,
        interval: RecordingInterval,
        price_path: str | Path,
        cprofile_lines: int = 20,
    ) -> tuple[pd.DataFrame, Dict[Tuple[str, str, int], str]]:
        """
        Minimal-diff version of your compare_strategies that:
          1) loads ticks once,
          2) runs each strategy exactly as before (print + persist),
          3) measures each run with timeit (default_timer), cProfile, memory_profiler.

        RETURNS:
          - DataFrame: strategy_name, dataset_label, n_ticks, total_time_s, peak_mem_mib
          - cprofile_map: {(strategy_name, dataset_label, n_ticks) -> hotspot text}
        """
        price_path = Path(price_path)
        ticks = self._load_ticks(price_path)
        print(f"Loaded {len(ticks)} market data points from {price_path}.")

        rows: List[MeasureRow] = []
        cprofile_map: Dict[Tuple[str, str, int], str] = {}
        dataset_label = self._infer_dataset_label(price_path)

        for strategy in strategies:
            strategy_name = strategy.__class__.__name__

            pr = cProfile.Profile()

            def _profiled_run():
                portfolio, metrics, periodic_returns, current_prices = self._run_engine_once(
                    strategy=strategy, cash=cash, failure_rate=failure_rate, interval=interval, ticks=ticks
                )
                self._print_portfolio_summary(portfolio, metrics, current_prices)
                self._persist_performance(strategy_name, metrics, periodic_returns)
                self._write_portfolio_history(
                    portfolio_history=[(ts, cash_val, hold_val) for (ts, cash_val, hold_val) in getattr(portfolio, "history", [])] 
                    if hasattr(portfolio, "history") else
                    [],
                    strategy_name=strategy_name
                )

            start = default_timer()
            if _HAS_MEMPROF:
                memory_usage((lambda: pr.runcall(_profiled_run),), interval=0.05, include_children=True)
                peak_mib = max(memory_usage((lambda: None,), max_iterations=1, include_children=True)) 
            else:
                pr.runcall(_profiled_run)
                peak_mib = None
            total_time_s = default_timer() - start        

            top = _cprofile_top_text(pr, lines=cprofile_lines)

            rows.append(MeasureRow(
                strategy_name=strategy_name,
                dataset_label=dataset_label,
                n_ticks=len(ticks),
                total_time_s=total_time_s,
                peak_mem_mib=peak_mib,
                cprofile_top=top,
            ))
            cprofile_map[(strategy_name, dataset_label, len(ticks))] = top
            
        df = pd.DataFrame([r.__dict__ for r in rows]).drop(columns=["cprofile_top"])
        return df.sort_values(["strategy_name", "n_ticks"]), cprofile_map
