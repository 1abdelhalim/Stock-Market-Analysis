import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# File paths
CSV_FILE_PATH = "/home/abdelhalim/Desktop/Temp /StockMarketAnalysis/data/tech_stocks.csv"

METRICS_FILE_PATH = "/home/abdelhalim/Desktop/Temp /StockMarketAnalysis/data/delta_tables/cleaned_tech_stocks/part-00000-32e1b63e-c912-4b62-b80e-ed23a65207ec-c000.snappy.parquet"

# Load data
@st.cache_data
def load_data():
    stock_data = pd.read_csv(CSV_FILE_PATH)

    # Check if the metrics file exists
    try:
        metrics_data = pd.read_parquet(METRICS_FILE_PATH)
    except FileNotFoundError:
        st.error("Metrics file not found. Please ensure the pipeline has generated the final metrics file.")
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
    col1.metric("Latest Closing Price", f"${filtered_stock_data['Close'].iloc[-1]:.2f}")
    col2.metric("Average Closing Price", f"${filtered_stock_data['Close'].mean():.2f}")
    col3.metric("Total Trading Volume", f"{filtered_stock_data['Volume'].sum():,}")

    # Essential Metrics
    st.subheader("Essential Metrics")
    st.markdown("### Metric Definitions")
    st.markdown("- **RSI (Relative Strength Index):** Measures the speed and change of price movements. Values above 70 indicate overbought conditions, while values below 30 indicate oversold conditions.")
    st.markdown("- **Sharpe Ratio:** Indicates the risk-adjusted return of an investment. Higher values are better.")

    col4, col5 = st.columns(2)
    if "RSI" in filtered_metrics_data.columns:
        col4.metric("RSI (Relative Strength Index)", f"{filtered_metrics_data['RSI'].iloc[-1]:.2f}")
    if "Sharpe_Ratio" in filtered_metrics_data.columns:
        col5.metric("Sharpe Ratio", f"{filtered_metrics_data['Sharpe_Ratio'].iloc[-1]:.2f}")

    # Visualizations
    st.subheader("Visualizations")
    st.plotly_chart(px.line(filtered_stock_data, x="Date", y="Close", title=f"{ticker} Closing Price"), use_container_width=True)

    if "MA_20" in filtered_metrics_data.columns:
        st.plotly_chart(px.line(filtered_metrics_data, x="Date", y="MA_20", title=f"{ticker} 20-Day Moving Average"), use_container_width=True)

    st.plotly_chart(px.bar(filtered_stock_data, x="Date", y="Volume", title=f"{ticker} Trading Volume"), use_container_width=True)

    # Insights
    st.subheader("Insights")
    st.write("Days with the highest trading volume:")
    st.write(filtered_stock_data.nlargest(5, "Volume"))

if __name__ == "__main__":
    main()