from pathlib import Path
from typing import List

import pandas as pd
import requests
import yfinance as yf
import csv
from datetime import datetime

from trading_lib.models import MarketDataPoint


SNP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


class PriceLoader:
    """Loads historical price data from Yahoo Finance."""

    def __init__(self, start_date: str, end_date: str, output_dir: str = "data/prices"):
        self.start_date = start_date
        self.end_date = end_date
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tickers: List[str] = []

    def _fetch_snp500_tickers(self) -> None:
        """Fetch list of S&P 500 tickers from Wikipedia."""
        # Add User-Agent header to avoid 403 error
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(SNP500_URL, headers=headers)
        response.raise_for_status()
        
        tables = pd.read_html(response.text)
        df = tables[0]  # First table contains the tickers
        self.tickers = df["Symbol"].tolist()

    def download_ticker(self, ticker: str, type: str = "csv") -> None:
        """Load historical data for a single ticker."""
        print(f"Downloading {ticker}...")
        try:
            data = yf.Ticker(ticker)
            hist = data.history(start=self.start_date, end=self.end_date)
            hist_prices = hist[["Close"]]

            # Drop rows with missing or sparse data
            hist_prices = hist_prices.dropna(subset=["Close"])
            expected_coverage = pd.date_range(start=self.start_date, end=self.end_date, freq='B')
            coverage = len(hist_prices) / len(expected_coverage)
            if coverage < 0.8:
                print(f"Warning: {ticker} has low data coverage ({coverage:.2%}). Skipping.")
                return
            
            # Save to CSV
            output_file = self.output_dir / f"{ticker}.{type}"
            
            match type:
                case "csv":
                    hist_prices.to_csv(output_file)
                case "parquet":
                    hist_prices.to_parquet(output_file)
                case _:
                    raise ValueError(f"Invalid type: {type}")
            
            print(f"Saved to {output_file}")
            
        except Exception as e:
            print(f"Error downloading {ticker}: {e}")

    def download_all_tickers(self, type: str = "csv") -> None:
        tickers = self._fetch_snp500_tickers()
        for ticker in tickers:
            self.download_ticker(ticker, type)
    
    def load_ticker_from_csv(self, ticker: str) -> List[MarketDataPoint]:
        """Load ticker data from CSV file and convert to MarketDataPoint objects."""
        csv_file = self.output_dir / f"{ticker}.csv"
        
        # Read CSV file
        df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
        
        hist_prices: List[MarketDataPoint] = []
        
        # Iterate through DataFrame rows and convert to MarketDataPoint
        for index, row in df.iterrows():
            try:
                mdp = MarketDataPoint(
                    timestamp=pd.to_datetime(index),
                    symbol=ticker,
                    price=float(row["Close"]),
                )
                hist_prices.append(mdp)
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping row {index}: {e}")
                continue
        
        return hist_prices
    
    def load_ticker_from_parquet(self, ticker: str) -> List[MarketDataPoint]:
        """Load ticker data from parquet file and convert to MarketDataPoint objects."""
        parquet_file = self.output_dir / f"{ticker}.parquet"
        
        # Read parquet file
        df = pd.read_parquet(parquet_file)
        
        hist_prices: List[MarketDataPoint] = []
        
        # Iterate through DataFrame rows and convert to MarketDataPoint
        for index, row in df.iterrows():
            try:
                mdp = MarketDataPoint(
                    timestamp=pd.to_datetime(index),
                    symbol=ticker,
                    price=float(row["Close"]),
                )
                hist_prices.append(mdp)
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping row {index}: {e}")
                continue
        
        return hist_prices

    
if __name__ == "__main__":
    loader = PriceLoader(start_date="2005-01-01", end_date="2024-12-31")
    tickers = ("ABNB", "AAPL")
    for ticker in tickers:
        loader.download_ticker(ticker, "csv")
        file_path = loader.output_dir / f"{ticker}.csv"
        if file_path.exists():
            data = loader.load_ticker_from_csv(file_path.stem)
            print(data)
        else:
            print("No data file found for {ticker} (likely skipped due to sparse data).")