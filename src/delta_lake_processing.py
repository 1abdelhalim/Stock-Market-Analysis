import pandas as pd
import os
from delta.tables import DeltaTable
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, stddev, lag, when, lit, last
from pyspark.sql.window import Window

DATA_DIR = "/home/abdelhalim/Desktop/Temp /StockMarketAnalysis/data/"
CSV_FILE_PATH = os.path.join(DATA_DIR, "tech_stocks.csv")
DELTA_TABLE_PATH = os.path.join(DATA_DIR, "delta_tables/tech_stocks")
CLEANED_DELTA_TABLE_PATH = os.path.join(DATA_DIR, "delta_tables/cleaned_tech_stocks")
FINAL_DELTA_TABLE_PATH = os.path.join(DATA_DIR, "delta_tables/final_tech_stocks")

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

def compute_financial_metrics():
    """Compute financial metrics and save the final dataset."""
    # Read cleaned data
    df = spark.read.format("delta").load(CLEANED_DELTA_TABLE_PATH)

    # Compute additional metrics
    window_spec = Window.partitionBy("Ticker").orderBy("Date")

    # Compute RSI (Relative Strength Index)
    df = df.withColumn("Change", col("Close") - lag("Close", 1).over(window_spec))
    df = df.withColumn("Gain", when(col("Change") > 0, col("Change")).otherwise(0))
    df = df.withColumn("Loss", when(col("Change") < 0, -col("Change")).otherwise(0))
    df = df.withColumn("Avg_Gain", avg("Gain").over(window_spec.rowsBetween(-13, 0)))
    df = df.withColumn("Avg_Loss", avg("Loss").over(window_spec.rowsBetween(-13, 0)))
    df = df.withColumn("RS", col("Avg_Gain") / col("Avg_Loss"))
    df = df.withColumn("RSI", 100 - (100 / (1 + col("RS"))))

    # Compute Sharpe Ratio
    df = df.withColumn("Daily_Return", (col("Close") - lag("Close", 1).over(window_spec)) / lag("Close", 1).over(window_spec))
    df = df.withColumn("Mean_Return", avg("Daily_Return").over(window_spec.rowsBetween(-19, 0)))
    df = df.withColumn("Std_Dev_Return", stddev("Daily_Return").over(window_spec.rowsBetween(-19, 0)))
    df = df.withColumn("Sharpe_Ratio", col("Mean_Return") / col("Std_Dev_Return"))

    # Save the final dataset
    df.write.format("delta").mode("overwrite").save(FINAL_DELTA_TABLE_PATH)

    print("✅ Financial metrics computed and saved.")

if __name__ == "__main__":
    load_csv_to_parquet()
    partition_data()
    clean_and_transform_data()
    compute_financial_metrics()
