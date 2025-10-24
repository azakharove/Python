from pathlib import Path
from typing import List

import pandas as pd
import requests
import yfinance as yf
import csv
from datetime import datetime
import time
import math

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
        df = tables[0]  # First table contains the ticker
        col = "Symbol" if "Symbol" in df.columns else df.columns[0]
        self.tickers = df[col].astype(str).str.replace(".", "-", regex=False).tolist()
        print(f"Fetched {len(self.tickers)} tickers from Wikipedia.")

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

    def clean_up_price_data(self, ticker: str, price_data):
        """ Clean sparse/missing data for one ticker."""
        # Normalize to a Series of Close
        if isinstance(price_data, pd.DataFrame):
            if "Close" in price_data.columns:
                s = price_data["Close"]
            elif "Adj Close" in price_data.columns:
                s = price_data["Adj Close"]
            elif price_data.shape[1] == 1:
                s = price_data.iloc[:, 0]
            else:
                raise ValueError(f"{ticker}: 'Close' column missing")
        else:
            s = price_data

        # Make sure it's numeric and drop NaNs
        s = pd.to_numeric(s, errors="coerce")
        s = s.dropna()

        # Wrap back to single-column DataFrame
        hist_prices = s.to_frame("Close")
        if hist_prices.index.name is None:
            hist_prices.index.name = "Date"

        # Coverage check (>= 80% of business days)
        expected = pd.date_range(start=self.start_date, end=self.end_date, freq="B")
        coverage = len(hist_prices) / len(expected)
        low_cov = coverage < 0.80
        if low_cov:
            print(f"Warning: {ticker} has low data coverage ({coverage:.2%}). Skipping.")

        return low_cov, hist_prices


            
    def save_data_to_file(self, ticker: str, hist_prices: pd.DataFrame, filetype: str = "csv") -> None:
        """Save ONE ticker's cleaned data (single 'Close' column)."""
        if "Close" not in hist_prices.columns or hist_prices.shape[1] != 1:
            hist_prices = hist_prices.iloc[:, [0]].copy()
            hist_prices.columns = ["Close"]
        if hist_prices.index.name is None:
            hist_prices.index.name = "Date"

        output_file = self.output_dir / f"{ticker}.{filetype}"
        try:
            if filetype == "csv":
                hist_prices.to_csv(output_file)
            elif filetype == "parquet":
                hist_prices.to_parquet(output_file)
            else:
                raise ValueError(f"Invalid filetype: {filetype}")
            print(f"Saved {ticker} → {output_file}")
        except Exception as e:
            print(f"Error saving {ticker}: {e}")

    def download_batch(self, batch: list[str], filetype="csv") -> None:
        try:
            # Download prices for all tickers in this batch
            df = yf.download(
                tickers=batch,
                start=self.start_date,
                end=self.end_date,
                group_by="column",
                progress=False,
                threads=True,
                auto_adjust=False,
            )


            # MultiIndex columns when multiple tickers
            if isinstance(df.columns, pd.MultiIndex):
                if "Close" not in df.columns.get_level_values(0):
                    print("Warning: result missing 'Close' level. Skipping batch.")
                    return
                close_df = df["Close"]  # columns = each ticker 
            else:
                close_df = pd.DataFrame({batch[0]: df["Close"]})

            for t in batch:
                if t not in close_df.columns:
                    print(f"Warning: {t} missing from result. Skipping.")
                    continue

                low_cov, hist_prices = self.clean_up_price_data(t, close_df[t])
                if not low_cov:
                    self.save_data_to_file(t, hist_prices, filetype)

        except Exception as e:
            print(f"Error downloading batch {batch}: {e}")


    def download_all_tickers(self, filetype="csv", batch_size = 50) -> None:
        "Load historical data for all tickers using server-side batching"

        for i in range(0, len(self.tickers), batch_size):
            batch = self.tickers[i : i + batch_size]
            print(f"Downloading batch {i+1}-{i+len(batch)} of {len(self.tickers)}...")
            try:
                self.download_batch(batch, filetype)
            except Exception as e:
                print(f"Error in batch ({i+1}-{i+len(batch)}):{e}")

        print("\n All batches complete")

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

    print("Fetching S&P 500 Tickers from Wikipedia")
    loader._fetch_snp500_tickers()          # <-- call it
    print(f"Fetched {len(loader.tickers)}.")
    print("Sample:", loader.tickers[:5])

    # Test cleanup + save on one ticker
    ticker1 = loader.tickers[3] if loader.tickers else "AAPL"
    print(f"\nCleanup and Save a single ticker: {ticker1}")
    try:
        df = yf.download(ticker1, start=loader.start_date, end=loader.end_date,
                        progress=False, auto_adjust=False)
        if df.empty:
            raise ValueError(f"{ticker1}: no data returned")

        # --- minimal robust selection of a close-like column ---
        if "Close" in df.columns:
            close_like = df["Close"]
        elif "Adj Close" in df.columns:
            close_like = df["Adj Close"]
        elif "close" in df.columns:
            close_like = df["close"]
        else:
            raise ValueError(f"{ticker1}: no close-like column found (cols={list(df.columns)})")

        # -------------------------------------------------------

        low_cov, hist_prices = loader.clean_up_price_data(ticker1, close_like)
        if not low_cov:
            loader.save_data_to_file(ticker1, hist_prices, "csv")

    except Exception as e:
        print(f"Error testing single-ticker cleanup/save: {e}")

    # Test batch
    print("\nTesting batch download on first 5 tickers...")
    batch = loader.tickers[:5] if len(loader.tickers) >= 5 else ["AAPL", "MSFT", "GOOG", "AMZN", "NVDA"]
    loader.download_batch(batch, filetype="csv")

    # Test all (limit to first 10 for speed)
    print("\nTesting download_all_tickers with batching...")
    loader.tickers = loader.tickers[:10]
    loader.download_all_tickers(filetype="csv", batch_size=3)

    print("\nMain 2.0 Complete")

    # tickers = ("ABNB", "AAPL")
    # for ticker in tickers:
    #     loader.download_ticker(ticker, "csv")
    #     file_path = loader.output_dir / f"{ticker}.csv"
    #     if file_path.exists():
    #         data = loader.load_ticker_from_csv(file_path.stem)
    #         print(data)
    #     else:
    #         print("No data file found for {ticker} (likely skipped due to sparse data).")

    # print("\nMain 1.0 Complete")
