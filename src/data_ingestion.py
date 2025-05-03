import yfinance as yf
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# fetches historical stock data for a list of technology companies
TICKERS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "META",  
    "TSLA", "NVDA", "PYPL", "INTC", "ADBE",
    "CSCO", "NFLX", "CRM", "AVGO", "QCOM",
    "IBM", "TXN", "UBER", "ORCL", "SAP"
]

from datetime import datetime, timedelta

# Get today's date
END_DATE = datetime.today().strftime("%Y-%m-%d")

# Get the date two years ago
START_DATE = (datetime.today() - timedelta(days=730)).strftime("%Y-%m-%d")

# Get paths from environment variables or use defaults
DATA_DIR = os.getenv("DATA_DIR", "data")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH", os.path.join(DATA_DIR, "tech_stocks.csv"))

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_stock_data(tickers=TICKERS):
    data = yf.download(tickers, start=START_DATE, end=END_DATE, group_by="ticker")

    all_data = []

    for ticker in tickers:
        if ticker in data:
            df = data[ticker].copy()
            df["Ticker"] = ticker  # Add ticker column
            df.reset_index(inplace=True)  # Move Date from index to column
            all_data.append(df)

    # Combine all stocks into a single DataFrame
    full_data = pd.concat(all_data, ignore_index=True)

    return full_data

# Add validation for timestamps, ticker formats, and price values
def validate_data(data):
    # Ensure timestamps are valid
    data = data[data['Date'].notnull()]

    # Validate ticker formats (e.g., non-empty strings)
    data = data[data['Ticker'].str.match(r'^[A-Z]+$')]

    # Validate price values (e.g., no negative prices)
    for col in ['Open', 'High', 'Low', 'Close']:
        data = data[data[col] >= 0]

    return data

# Save the data to a CSV file
def save_data_to_csv(data, file_path=CSV_FILE_PATH):
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    data.to_csv(file_path, index=False)
    print(f"✅ Data saved to {file_path}")

if __name__ == "__main__":
    # Fetch the data
    stock_data = fetch_stock_data(TICKERS)
    validated_data = validate_data(stock_data)

    # Save the fetched data to a CSV file
    save_data_to_csv(validated_data, CSV_FILE_PATH)
