import pandas as pd
import os
from delta.tables import DeltaTable
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, stddev, lag, when, lit, last
from pyspark.sql.window import Window
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get paths from environment variables or use defaults
DATA_DIR = os.getenv("DATA_DIR", "data")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH", os.path.join(DATA_DIR, "tech_stocks.csv"))
DELTA_TABLE_PATH = os.getenv("DELTA_TABLE_PATH", os.path.join(DATA_DIR, "delta_tables/tech_stocks"))
CLEANED_DELTA_TABLE_PATH = os.getenv("CLEANED_DELTA_TABLE_PATH", os.path.join(DATA_DIR, "delta_tables/cleaned_tech_stocks"))
FINAL_DELTA_TABLE_PATH = os.getenv("FINAL_DELTA_TABLE_PATH", os.path.join(DATA_DIR, "delta_tables/final_tech_stocks"))

# Ensure directories exist
for path in [os.path.dirname(CSV_FILE_PATH), DELTA_TABLE_PATH, CLEANED_DELTA_TABLE_PATH, FINAL_DELTA_TABLE_PATH]:
    os.makedirs(path, exist_ok=True)

# Spark session with Delta Lake
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("StockDataProcessing") \
    .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()


def load_csv_to_parquet():
    df = pd.read_csv(CSV_FILE_PATH)

    df.fillna(method='ffill', inplace=True)

    # Convert 'Date' column to datetime
    df['Date'] = pd.to_datetime(df['Date'])

    # Add new columns for analysis
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    df['DayOfWeek'] = df['Date'].dt.dayofweek

    spark_df = spark.createDataFrame(df)

    spark_df.write.format("parquet").mode("overwrite").save(DELTA_TABLE_PATH)

    print(f"✅ Data saved in Parquet format at {DELTA_TABLE_PATH}")

def partition_data():
    """Partition data by Ticker and Year-Month."""
    # Read data from Delta Lake instead of CSV
    df = spark.read.format("delta").load(DELTA_TABLE_PATH)

    # Add Year-Month column for partitioning
    df = df.withColumn("YearMonth", df["Date"].substr(0, 7))

    # Write to Delta Lake with partitioning
    df.write.format("delta").partitionBy("Ticker", "YearMonth").mode("overwrite").save(DELTA_TABLE_PATH)

    print("✅ Data partitioned and saved in Delta Lake format.")

def clean_and_transform_data():
    """Clean and transform data: deduplication, missing value handling, and technical indicators."""
    # Read data from Delta Lake
    delta_table = DeltaTable.forPath(spark, DELTA_TABLE_PATH)
    df = delta_table.toDF()

    # Deduplicate records
    df = df.dropDuplicates()

    # Handle missing values (forward-fill using last)
    window_spec = Window.partitionBy("Ticker").orderBy("Date")
    for col_name in ["Open", "High", "Low", "Close", "Volume"]:
        df = df.withColumn(col_name, last(col_name, ignorenulls=True).over(window_spec))

    # Add technical indicators (e.g., Moving Averages, Volatility)
    df = df.withColumn("MA_5", avg("Close").over(window_spec.rowsBetween(-4, 0)))
    df = df.withColumn("Volatility", stddev("Close").over(window_spec.rowsBetween(-4, 0)))

    # Write cleaned and transformed data back to Delta Lake
    df.write.format("delta").mode("overwrite").save(CLEANED_DELTA_TABLE_PATH)

    print("✅ Data cleaned, transformed, and saved in Delta Lake format.")

if __name__ == "__main__":
    load_csv_to_parquet()
    partition_data()
    clean_and_transform_data()
    compute_financial_metrics()
