# CSV-Based Algorithmic Trading Backtester

## Setup

Install the trading library in editable mode:
```bash
pip install -e .
```

This makes `trading_lib` available for import across all assignments.

## Usage

Run the backtester for Assignment1:
```bash
python Assignment1/main.py
```

Run with custom arguments:
```bash
python Assignment1/main.py -c 50000 -q 100 -f 0.1 -d data/market_data.csv
```

### Command-Line Arguments

- `-d`, `--csv_path`: Path to the market data CSV file (default: `data/market_data.csv`)
- `-q`, `--quantity`: Number of shares per trade (default: `10`)
- `-f`, `--failure_rate`: Simulated order failure rate as decimal (default: `0.05` = 5%)
- `-c`, `--cash`: Initial portfolio cash (default: `100000`)
- `-i`, `--interval`: Portfolio recording interval (default: `1s`)
  - Options: `tick`, `1s`, `1m`, `1h`, `1d`, `1mo`

## Testing

Run all tests:
```bash
python -m pytest test/
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

## Project Structure

```
Python/
├── pyproject.toml          # Package configuration
├── trading_lib/            # Reusable library
│   ├── models.py          # Data models (Order, MarketDataPoint, etc.)
│   ├── portfolio.py       # Portfolio management
│   ├── engine.py          # Execution engine
│   ├── strategy.py        # Base strategy class
│   ├── exceptions.py      # Custom exceptions
│   └── reporting.py       # Performance reporting
├── Assignment1/           # Assignment-specific code
│   ├── main.py           # Entry point
│   ├── strategies.py     # Trading strategies
│   └── data_loader.py    # Data loading utilities
└── test/                 # Unit tests
```

## Output

After running, the backtester generates:
- `performance.md` - Detailed performance report with metrics
- `equity_curve.png` - Visual chart of portfolio value over time
