import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os
import glob
from dotenv import load_dotenv
import seaborn as sns
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()

# File paths - use environment variables or defaults
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH", "data/tech_stocks.csv")
CLEANED_DELTA_TABLE_PATH = os.getenv("CLEANED_DELTA_TABLE_PATH", "data/delta_tables/cleaned_tech_stocks")

# Load data
@st.cache_data
def load_data():
    # Load stock data from CSV
    if not os.path.exists(CSV_FILE_PATH):
        st.error(f"Stock data file not found at {CSV_FILE_PATH}. Please run the data ingestion pipeline first.")
        st.stop()
    
    stock_data = pd.read_csv(CSV_FILE_PATH)
    
    # Find parquet files in the cleaned delta table directory
    if not os.path.exists(CLEANED_DELTA_TABLE_PATH):
        st.error(f"Metrics directory not found at {CLEANED_DELTA_TABLE_PATH}. Please run the data processing pipeline first.")
        st.stop()
    
    # Find the first parquet file in the directory
    parquet_files = glob.glob(os.path.join(CLEANED_DELTA_TABLE_PATH, "*.parquet"))
    if not parquet_files:
        parquet_files = glob.glob(os.path.join(CLEANED_DELTA_TABLE_PATH, "**/*.parquet"))
    
    if not parquet_files:
        st.error("No metrics files found. Please ensure the pipeline has generated the metrics files.")
        st.stop()
    
    metrics_file_path = parquet_files[0]
    
    # Load metrics data from parquet
    try:
        metrics_data = pd.read_parquet(metrics_file_path)
    except Exception as e:
        st.error(f"Error loading metrics data: {e}")
        st.stop()

    # Convert 'Date' column to datetime
    stock_data['Date'] = pd.to_datetime(stock_data['Date'])
    metrics_data['Date'] = pd.to_datetime(metrics_data['Date'])

    return stock_data, metrics_data

# Main app
def main():
    st.set_page_config(page_title="Stock Market Dashboard", layout="wide")
    st.title("📈 Stock Market Analysis Dashboard")

    # Load data
    stock_data, metrics_data = load_data()

    # Sidebar filters
    st.sidebar.header("Filters")
    ticker = st.sidebar.selectbox("Select Ticker", stock_data["Ticker"].unique())

    min_date = stock_data["Date"].min()
    max_date = stock_data["Date"].max()
    date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

    # Convert date_range to datetime64[ns]
    date_range = [pd.to_datetime(date) for date in date_range]

    # Filter data
    filtered_stock_data = stock_data[(stock_data["Ticker"] == ticker) & (stock_data["Date"] >= date_range[0]) & (stock_data["Date"] <= date_range[1])]
    filtered_metrics_data = metrics_data[(metrics_data["Ticker"] == ticker) & (metrics_data["Date"] >= date_range[0]) & (metrics_data["Date"] <= date_range[1])]

    # Overview
    st.subheader("Overview")
    col1, col2, col3 = st.columns(3)
    
    if not filtered_stock_data.empty:
        col1.metric("Latest Closing Price", f"${filtered_stock_data['Close'].iloc[-1]:.2f}")
        col2.metric("Average Closing Price", f"${filtered_stock_data['Close'].mean():.2f}")
        col3.metric("Total Trading Volume", f"{filtered_stock_data['Volume'].sum():,}")
    else:
        st.warning("No data available for the selected filters.")
        st.stop()

  

    col4, col5 = st.columns(2)
    if "RSI" in filtered_metrics_data.columns and not filtered_metrics_data.empty:
        col4.metric("RSI (Relative Strength Index)", f"{filtered_metrics_data['RSI'].iloc[-1]:.2f}")
    if "Sharpe_Ratio" in filtered_metrics_data.columns and not filtered_metrics_data.empty:
        col5.metric("Sharpe Ratio", f"{filtered_metrics_data['Sharpe_Ratio'].iloc[-1]:.2f}")

    # Visualizations
    st.subheader("Visualizations")
    
    # RSI Visualization
    if "RSI" in filtered_metrics_data.columns and not filtered_metrics_data.empty:
        st.plotly_chart(px.line(filtered_metrics_data, x="Date", y="RSI", title=f"{ticker} RSI (Relative Strength Index)"), use_container_width=True)

    # Sharpe Ratio Visualization
    if "Sharpe_Ratio" in filtered_metrics_data.columns and not filtered_metrics_data.empty:
        st.plotly_chart(px.line(filtered_metrics_data, x="Date", y="Sharpe_Ratio", title=f"{ticker} Sharpe Ratio"), use_container_width=True)

    # Existing Moving Average Visualization
    if "MA_20" in filtered_metrics_data.columns and not filtered_metrics_data.empty:
        st.plotly_chart(px.line(filtered_metrics_data, x="Date", y="MA_20", title=f"{ticker} 20-Day Moving Average"), use_container_width=True)

    st.plotly_chart(px.bar(filtered_stock_data, x="Date", y="Volume", title=f"{ticker} Trading Volume"), use_container_width=True)

    # Add Volatility Analysis
    st.subheader("Volatility Analysis")
    if not filtered_stock_data.empty:
        filtered_stock_data['Daily_Volatility'] = filtered_stock_data['High'] - filtered_stock_data['Low']
        st.metric("Average Daily Volatility", f"${filtered_stock_data['Daily_Volatility'].mean():.2f}")

    # Add Top Gainers/Losers
    st.subheader("Top Gainers and Losers")
    filtered_stock_data['Daily_Change'] = (filtered_stock_data['Close'] - filtered_stock_data['Open']) / filtered_stock_data['Open'] * 100
    st.write("**Top 3 Gainers:**")
    st.write(filtered_stock_data.nlargest(3, 'Daily_Change')[['Date', 'Ticker', 'Daily_Change']])
    st.write("**Top 3 Losers:**")
    st.write(filtered_stock_data.nsmallest(3, 'Daily_Change')[['Date', 'Ticker', 'Daily_Change']])

    # Add Correlation Heatmap (if multiple tickers are selected)
    st.subheader("Correlation Heatmap")
    if len(stock_data['Ticker'].unique()) > 1:
        pivot_data = stock_data.pivot(index='Date', columns='Ticker', values='Close')
        correlation_matrix = pivot_data.corr()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    # Add Trendline to Closing Price Chart
    st.subheader("Trend Analysis")
    fig = px.scatter(filtered_stock_data, x="Date", y="Close", trendline="ols", title=f"{ticker} Closing Price with Trendline")
    st.plotly_chart(fig, use_container_width=True)

    # Insights
    st.subheader("Insights")
    st.write("Days with the highest trading volume:")
    st.write(filtered_stock_data.nlargest(5, "Volume"))

if __name__ == "__main__":
    main()