# CSV-Based Algorithmic Trading Backtester

## Usage

Run the backtester with default settings:
```bash
python main.py
```

Run with custom arguments:
```bash
python main.py -c 50000 -q 100 -f 0.1 -d data/market_data.csv
```

### Command-Line Arguments

- `-d`, `--csv_path`: Path to the market data CSV file (default: `data/market_data.csv`)
- `-q`, `--quantity`: Number of shares per trade (default: `10`)
- `-f`, `--failure_rate`: Simulated order failure rate as decimal (default: `0.05` = 5%)
- `-c`, `--cash`: Initial portfolio cash (default: `100000`)

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
