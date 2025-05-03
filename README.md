# Stock Market Analysis

## Overview
This project provides a comprehensive pipeline for analyzing stock market data using PySpark and Delta Lake. It processes stock market data, computes financial metrics, and visualizes insights through a Streamlit dashboard.

## Features
- **Data Ingestion**: Collects stock data from Yahoo Finance API
- **Data Processing**: Cleans data and computes technical indicators (Moving Averages, RSI, Sharpe Ratio)
- **Data Storage**: Efficiently stores data using Delta Lake format
- **Visualization**: Interactive dashboard with Streamlit
- **Automation**: Workflow orchestration with Apache Airflow

## Tech Stack
- **Processing**: PySpark, Python
- **Storage**: Delta Lake
- **Visualization**: Streamlit, Plotly
- **Orchestration**: Apache Airflow
- **APIs**: Yahoo Finance
- **Containerization**: Docker

## Project Structure
```
StockMarketAnalysis/
├── data/               # Raw and processed data
│   └── delta_tables/   # Delta Lake tables
├── notebooks/          # Jupyter notebooks for exploration
├── src/                # Source code
├── airflow/            # Airflow DAGs
│   └── dags/           # DAG definitions
├── Dockerfile          # Docker configuration
├── requirements.txt    # Dependencies
└── README.md           # Documentation
```

## Setup Instructions

### Local Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/stock-market-analysis.git
   cd stock-market-analysis
   ```

2. **Install Dependencies**:
   ```bash
   python -m venv stock
   source stock/bin/activate  # On Windows: stock\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the Pipeline**:
   ```bash
   python src/data_ingestion.py
   python src/delta_lake_processing.py
   python src/streamlit_dashboard.py
   ```

### Docker Setup
1. **Build the Docker Image**:
   ```bash
   docker build -t stock-market-analysis .
   ```

2. **Run the Docker Container**:
   ```bash
   docker run -p 8501:8501 stock-market-analysis
   ```

3. **Access the Dashboard**:
   Open your browser and navigate to `http://localhost:8501`

## Financial Metrics
The analysis includes:
- Moving Averages (20-day)
- Relative Strength Index (RSI)
- Sharpe Ratio
- Daily Returns

## License
[MIT License](LICENSE)
````

## Contact
For questions or contributions, please reach out via GitHub.
