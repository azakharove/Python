from trading_lib.strategy import Strategy
from trading_lib.models import RecordingInterval, MarketDataPoint
from trading_lib.engine import ExecutionEngine
from trading_lib.portfolio import Portfolio
from trading_lib.reporting import generate_performance_report, calc_performance_metrics
from trading_lib.data_loader import load_market_data, load_market_data_yf

import os
from datetime import datetime
import csv

import timeit
import cProfile
import memory_profiler

class StrategyProfiler:
    def __init__(self, output_path: str = ""):
        self.output_path = output_path
    
    def profile_strategies(
        self, 
        strategies: list[Strategy], 
        cash: float, 
        failure_rate: float, 
        interval: RecordingInterval, 
        price_path: str
    ):
        if os.path.isfile(price_path):
            ticks = load_market_data(price_path)
        elif os.path.isdir(price_path):
            ticks = load_market_data_yf(price_path)
        else:
            raise ValueError(f"Invalid price path: {price_path}")
    
        print(f"Loaded {len(ticks)} market data points.")

        self.performance_reports_for_strategies(strategies, cash, failure_rate, interval, ticks)

    def print_portfolio_summary(self, portfolio: Portfolio, metrics: dict, current_prices: dict[str, float]):
        holdings = portfolio.get_all_holdings()
        holdings_value = metrics['final_value'] - portfolio.get_cash()

        print(f"\n{'='*60}")
        print(f"FINAL PORTFOLIO SUMMARY")
        print(f"{'='*60}")
        print(f"Initial capital:     ${metrics['starting_value']:,.2f}")
        print(f"Final cash:          ${portfolio.get_cash():,.2f}")
        print(f"Holdings value:      ${holdings_value:,.2f}")
        print(f"Total portfolio:     ${metrics['final_value']:,.2f}")
        print(f"P&L:                 ${metrics['pnl']:,.2f} ({metrics['total_return']:+.2f}%)")
        print(f"\n{'='*60}")
        print(f"PERFORMANCE METRICS")
        print(f"{'='*60}")
        print(f"Sharpe Ratio:        {metrics['sharpe_ratio']:.2f}")
        print(f"Max Drawdown:        {metrics['max_drawdown']:.2f}%")
        
        if holdings:
            print(f"\n{'='*60}")
            print(f"CURRENT HOLDINGS")
            print(f"{'='*60}")
            for symbol, holding in holdings.items():
                price = current_prices.get(symbol, 0)
                position_value = holding["quantity"] * price
                print(f"  {symbol}: {holding['quantity']} shares @ ${price:.2f} = ${position_value:,.2f}")

    def output_filename(self, strategy_name: str, suffix: str) -> str:
        output_file = strategy_name + suffix
        if self.output_path != "":
            output_file = self.output_path + "/" + output_file
        return output_file

    def performance_reports_for_strategies(
        self, 
        strategies: list[Strategy], 
        cash: float, 
        failure_rate: float, 
        interval: RecordingInterval, 
        ticks: list[MarketDataPoint]
    ):
        
        for strategy in strategies:
            portfolio = Portfolio(cash=cash)
            strategy_name = strategy.__class__.__name__

            engine = ExecutionEngine(strategy, portfolio, failure_rate, recording_interval=interval)

            cProfile.runctx(
                'engine.process_ticks(ticks)',
                globals(),
                locals(), 
                filename = self.output_filename(strategy_name, "_cprofile.prof"))
            
            final_timestamp = ticks[-1].timestamp
            engine.record_final_state(final_timestamp)

            current_prices = engine.get_current_prices()
            periodic_returns = engine.get_portfolio_history()
            metrics = calc_performance_metrics(portfolio, cash, ticks, current_prices, periodic_returns)

            self.print_portfolio_summary(portfolio, metrics, current_prices)
                
            generate_performance_report(metrics, periodic_returns, self.output_filename(strategy_name,"_performance.md"))
            self.write_portfolio_history(engine.portfolio_history, strategy_name)

    def write_portfolio_history(self, portfolio_history: list[tuple[datetime, float, float]], strategy_name: str):
        output_file = strategy_name + "_portfolio_history.csv"
        if self.output_path != "":
            output_file = self.output_path + "/" + output_file
        with open(output_file, "w") as csv.csvfile:
            csv_writer = csv.writer(csv.csvfile)
            csv_writer.writerow(["Timestamp", "Cash", "Holdings"])
            csv_writer.writerows(portfolio_history)