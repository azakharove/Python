# CSV-Based Algorithmic Trading Backtester

An algorithmic trading backtesting framework with a shared library and assignment-specific implementations.

## Setup

Install the trading library in editable mode:
```bash
pip install -e .
```

This makes `trading_lib` available for import across all assignments.

## Project Structure

```
Python/
├── pyproject.toml                 # Package configuration
├── trading_lib/                   # Shared reusable library
│   ├── models.py                 # Data models (Order, MarketDataPoint, etc.)
│   ├── portfolio.py              # Portfolio management
│   ├── engine.py                 # Execution engine
│   ├── strategy.py               # Base strategy class
│   ├── exceptions.py             # Custom exceptions
│   ├── reporting.py              # Performance reporting
│   ├── data_loader.py            # Data loading utilities
│   ├── StrategyComparator.py     # Multi-strategy comparison
│   └── data_generator.py         # Market data generation
├── Assignment1/                    # Assignment 1: Basic strategies
│   ├── main.py                  # Entry point
│   └── trading_lib/             # Local library copy (legacy)
├── Assignment2/                  # Assignment 2: Advanced strategies comparison
│   ├── main.py                  # Run all strategies and generate reports
│   ├── BenchmarkStrategy.py     # Buy-and-hold baseline
│   ├── MovingAverageStrategy.py # Moving average crossover
│   ├── RSIStrategy.py           # RSI-based strategy
│   ├── MACDStrategy.py          # MACD momentum strategy
│   ├── VolatilityBreakoutStrategy.py # Volatility breakout trading
│   ├── PriceLoader.py           # Price data utilities
│   └── StrategyComparison.ipynb  # Interactive analysis notebook
├── Assignment_2_Results/         # Generated performance reports
│   ├── *_performance.md         # Performance summaries
│   ├── *_portfolio_history.csv  # Portfolio state over time
│   └── equity_curve.png         # Equity curves
├── data/                        # Market data
│   ├── market_data.csv          # Main market data file
│   └── prices/                  # Individual stock price files
└── test/                        # Unit tests
```

## Usage

### Assignment 2: Run Strategy Comparison

Compare multiple trading strategies:
```bash
cd Assignment2
python main.py
```

Run with custom arguments:
```bash
python main.py -c 1000000 -q 100 -f 0.0 -d ../data/market_data.csv
```

### Assignment 1: Basic Backtesting

Run the basic backtester:
```bash
python Assignment1/main.py
```

### Command-Line Arguments

- `-d`, `--csv_path`: Path to the market data CSV file (default: `data/market_data.csv`)
- `-q`, `--quantity`: Number of shares per trade (default: `10`)
- `-f`, `--failure_rate`: Simulated order failure rate as decimal (default: `0.0` = 0%)
- `-c`, `--cash`: Initial portfolio cash (default: `1000000`)
- `-i`, `--interval`: Portfolio recording interval (default: `tick`)
  - Options: `tick`, `1s`, `1m`, `1h`, `1d`, `1mo`

## Strategy Comparison Analysis

After running Assignment 2, open the Jupyter notebook for detailed analysis:
```bash
cd Assignment2
jupyter notebook StrategyComparison.ipynb
```

The notebook includes:
- Portfolio value over time across all strategies
- Cumulative PnL comparison
- Individual strategy breakdowns (cash, holdings, total value)
- Performance summaries and insights

## Output

After running Assignment 2, the backtester generates in `Assignment_2_Results/`:

- `*_performance.md` - Detailed performance reports with:
  - Summary metrics (return, Sharpe ratio, max drawdown)
  - Performance interpretations
  - Equity curve charts
  
- `*_portfolio_history.csv` - Portfolio state over time:
  - Timestamp, Cash, Holdings values at each interval

## Trading Strategies

### Benchmark Strategy
Simple buy-and-hold baseline for comparison.

### Moving Average Strategy
Uses 20-day and 50-day moving average crossovers to generate buy signals.

### RSI Strategy
Implements Relative Strength Index (RSI) to buy during oversold conditions (RSI < 30).

### MACD Strategy
Uses MACD (Moving Average Convergence Divergence) for momentum-based trading signals.

### Volatility Breakout Strategy
Identifies and trades on volatility breakouts in price movements.

## Testing

Run all tests:
```bash
pytest test/
```

Run specific test files:
```bash
pytest test/portfolio_test.py
pytest test/engine_test.py
pytest test/strategies_test.py
```

## Code Quality

Format code with Black:
```bash
black .
```

Check code with Ruff linter:
```bash
ruff check .
```

Auto-fix issues:
```bash
ruff check --fix .
```
