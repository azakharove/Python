import csv
from pathlib import Path
from datetime import datetime
from typing import List
from models import MarketDataPoint


def _parse_timestamp(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts)
    except ValueError as e:
        raise ValueError(f"Invalid timestamp format: {ts}") from e
       
def load_market_data(file_path: Path):
    """
    Loads market data from a CSV file,
    parse each row into a MarketDataPoint,
    collects them into a list, and returns the list.

    :param file_path: Path to the CSV file.
    :yield: MarketDataPoint(timestamp, symbol, price)
    """
    with file_path.open("r", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        required_format = {"timestamp", "symbol", "price"}
        if set(reader.fieldnames) != required_format:
            raise ValueError(f"CSV must have columns: {required_format}")
        market_data_list: List[MarketDataPoint] = []
        for row in reader:
            try:
                mdp = MarketDataPoint(
                    timestamp = _parse_timestamp(row["timestamp"]),
                    symbol = row["symbol"],
                    price = float(row["price"])
                )
            except ValueError as e:
                raise ValueError(f"Error parsing line {reader.line_num}: {e}") from e
            market_data_list.append(mdp)
        return market_data_list  

    
