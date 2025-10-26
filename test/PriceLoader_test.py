from Assignment2.PriceLoader import PriceLoader

import pandas as pd
import yfinance as yf

def test_fetch_snp500_tickers():
    loader = PriceLoader(start_date="2005-01-01", end_date="2024-12-31")
    loader._fetch_snp500_tickers()
    assert len(loader.tickers) > 0
    print(f"Fetched {len(loader.tickers)} S&P 500 tickers.")
    print("Sample tickers:", loader.tickers[:5])

def test_download_ticker():
    loader = PriceLoader(start_date="2005-01-01", end_date="2024-12-31")
    ticker = "AAPL"
    loader.download_ticker(ticker, type="csv")
    file_path = loader.output_dir / f"{ticker}.csv"
    if file_path.exists():
        print(f"Data saved to {file_path}.")
        data= loader.load_ticker_from_csv(ticker)
        print(data)
    else:
        print(f"No data file found for {ticker}.")

def test_clean_up_price_data():
    loader = PriceLoader(start_date="2005-01-01", end_date="2024-12-31")
    ticker = "AAPL"
    df = yf.download(ticker, start=loader.start_date, end=loader.end_date,
                     progress=False, auto_adjust=False)
    if df.empty:
        raise ValueError(f"{ticker}: no data returned")
    close_like = df["Close"] if "Close" in df.columns else df["Adj Close"]
    low_cov, hist_prices = loader.clean_up_price_data(ticker, close_like)
    assert isinstance(low_cov, bool)
    assert isinstance(hist_prices, pd.DataFrame)
    print(f"Cleaned up data for {ticker}, low_cov={low_cov}, {len(hist_prices)} prices.")

def test_save_data_to_file():
    loader = PriceLoader(start_date="2005-01-01", end_date="2024-12-31")
    ticker = "AAPL"
    df = yf.download(ticker, start=loader.start_date, end=loader.end_date,
                     progress=False, auto_adjust=False)
    close_like = df["Close"] if "Close" in df.columns else df["Adj Close"]
    low_cov, hist_prices = loader.clean_up_price_data(ticker, close_like)
    if not low_cov:
        loader.save_data_to_file(ticker, hist_prices, "csv")
        file_path = loader.output_dir / f"{ticker}.csv"
        assert file_path.exists()
        print(f"Saved cleaned data for {ticker} to {file_path}.")

def test_download_batch():
    loader = PriceLoader(start_date="2005-01-01", end_date="2024-12-31")
    tickers = ["AAPL", "MSFT", "GOOG"]
    loader.download_batch(tickers, filetype="csv")
    for ticker in tickers:
        file_path = loader.output_dir / f"{ticker}.csv"
        assert file_path.exists()
    print(f"Downloaded and saved batch of {len(tickers)} tickers.")

def test_download_all_tickers():
    loader = PriceLoader(start_date="2005-01-01", end_date="2024-12-31")
    loader.tickers = loader.tickers[:5]  # Limit to first 5 for testing
    loader.download_all_tickers(filetype="csv", batch_size=2)
    for ticker in loader.tickers:
        file_path = loader.output_dir / f"{ticker}.csv"
        assert file_path.exists()
    print(f"Downloaded and saved all tickers in batches.")