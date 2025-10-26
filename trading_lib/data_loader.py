import csv
from datetime import datetime
from pathlib import Path
from typing import List
import os

from trading_lib.models import MarketDataPoint


def _parse_timestamp(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts)
    except ValueError as e:
        raise ValueError(f"Invalid timestamp format: '{ts}'") from e

def _parse_date_only(ts: str) -> datetime:
    try:
        return datetime.strptime(ts, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format: '{ts}'") from e

def load_market_data(file_path: Path):
    """
    Loads market data from a CSV file,
    parse each row into a MarketDataPoint,
    collects them into a list, and returns the list.

    :param file_path: Path to the CSV file.
    :yield: MarketDataPoint(timestamp, symbol, price)
    """
    with file_path.open("r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        required_format = {"timestamp", "symbol", "price"}
        if set(reader.fieldnames) != required_format:
            raise ValueError(f"CSV must have columns: {required_format}")
        return load_from_reader(reader)

def load_from_reader(reader: csv.DictReader):
    market_data_list: List[MarketDataPoint] = []
    for row in reader:
        try:
            mdp = MarketDataPoint(
                timestamp=_parse_timestamp(row["timestamp"]),
                symbol=row["symbol"],
                price=float(row["price"]),
            )
        except ValueError as e:
            raise ValueError(f"Error parsing line {reader.line_num}: {e}") from e
        market_data_list.append(mdp)
    return market_data_list

def load_market_data_yf(directory_path: Path) -> List[MarketDataPoint]:
    """
    Loads market data from yf CSV files in a directory,
    parse each row into a MarketDataPoint,
    collects them into a list, and returns the list
    """
    market_data: List[MarketDataPoint] = []
    print(f"Loading price data from '{directory_path}'")
    for directory_entry in os.listdir(directory_path):
        full_path = os.path.join(directory_path, directory_entry) 
        print(f"Looking at '{directory_entry}' at '{full_path}'")
        if os.path.isfile(full_path) and directory_entry.endswith(".csv"):
            market_data.extend(read_yf_price_file(full_path))
    return market_data

def read_yf_price_file(full_path: str) -> List[MarketDataPoint]:
    with open(full_path, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        required_format = {"Date", "Close"}
        if set(reader.fieldnames) != required_format:
            raise ValueError(f"CSV must have columns: {required_format}")
        symbol = Path(full_path).stem  # Filename without extension as symbol
        return load_from_reader_yf(reader, symbol)

def load_from_reader_yf(reader: csv.DictReader, symbol: str) -> List[MarketDataPoint]:
    """
    Loads market data from a CSV DictReader,
    parse each row into a MarketDataPoint
    for files from yf
    """
    market_data_list: List[MarketDataPoint] = []
    for row in reader:
        try:
            mdp = MarketDataPoint(
                timestamp=_parse_date_only(row["Date"]),
                symbol=symbol,
                price=float(row["Close"]),
            )
        except ValueError as e:
            raise ValueError(f"Error parsing line {reader.line_num}: {e}") from e
        market_data_list.append(mdp)
    print(f"     Loaded {len(market_data_list)} data points for symbol '{symbol}'")
    return market_data_list

if __name__ == "__main__":
    # Example usage
    example = read_yf_price_file("data/prices/IBM.csv")
    print(len(example))
    print(example[0])
    print(example[1])
    
    