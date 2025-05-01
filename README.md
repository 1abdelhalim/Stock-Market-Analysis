# Stock Market Analysis

## Overview
This project provides a comprehensive pipeline for analyzing stock market data. It automates data collection, processing, and visualization to generate actionable insights.

## Features
- **Data Ingestion**: Collects stock data from APIs like Yahoo Finance.
- **Data Processing**: Cleans data, handles missing values, and computes technical indicators (e.g., Moving Averages, RSI).
- **Data Storage**: Efficiently stores data using Delta Lake.
- **Visualization**: Real-time dashboards with Apache Superset.
- **Automation**: Workflow orchestration with Apache Airflow.

## Tech Stack
- **Orchestration**: Apache Airflow
- **Storage**: Delta Lake
- **Processing**: PySpark, Python
- **Visualization**: Apache Superset
- **APIs**: Yahoo Finance

## Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/stock-market-analysis.git
   cd stock-market-analysis
   ```
2. **Install Dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Run the Pipeline**:
   ```bash
   python src/data_ingestion.py
   python src/delta_lake_processing.py
   python src/streamlit_dashboard.py
   ```

## Running with Docker

To run this project using Docker, follow these steps:

1. **Build the Docker Image**:
   ```bash
   docker build -t stock-market-analysis .
   ```

2. **Run the Docker Container**:
   ```bash
   docker run -p 8501:8501 stock-market-analysis
   ```

3. **Access the Dashboard**:
   Open your browser and navigate to `http://localhost:8501` to view the Streamlit dashboard.

## Directory Structure
```
stock-market-analysis/
├── data/               # Raw and processed data
├── notebooks/          # Jupyter notebooks for exploration
├── src/                # Source code for ingestion, processing, and visualization
├── airflow/            # Airflow DAGs
├── requirements.txt    # Dependencies
└── README.md           # Documentation
```

## Contact
For questions or contributions, please reach out via GitHub.
