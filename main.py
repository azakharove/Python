from pathlib import Path
import data_generator 
import data_loader


def main():
    csv_path = Path("market_data.csv")
    #data_generator.generate_market_csv(csv_path)
    ticks = data_loader.load_market_data(csv_path)
    print(f"Loaded {len(ticks)} market data points.")

if __name__ == "__main__":
    main()

