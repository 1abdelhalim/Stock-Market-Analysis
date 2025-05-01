import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, lit, sum, mean, stddev, lag, when
from pyspark.sql.window import Window
from delta.tables import DeltaTable

# Initialize Spark session
spark = SparkSession.builder \
    .appName("FinancialMetrics") \
    .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Define paths
CLEANED_DELTA_TABLE_PATH = "/home/abdelhalim/Desktop/Temp /StockMarketAnalysis/data/delta_tables/cleaned_tech_stocks"
FINAL_DELTA_TABLE_PATH = "/home/abdelhalim/Desktop/Temp /StockMarketAnalysis/data/delta_tables/tech_stocks"

# Ensure the output directory exists
if not os.path.exists(FINAL_DELTA_TABLE_PATH):
    os.makedirs(FINAL_DELTA_TABLE_PATH)
    print(f"✅ Created directory: {FINAL_DELTA_TABLE_PATH}")

def compute_financial_metrics():
    """
    Compute financial metrics such as Moving Averages, RSI, and Sharpe Ratio.
    Save the final dataset to Delta Lake.
    """
    # Read cleaned data from Delta Lake
    df = spark.read.format("delta").load(CLEANED_DELTA_TABLE_PATH)

    # Define a window specification for calculations
    window_spec = Window.partitionBy("Ticker").orderBy("Date")

    # Compute Moving Average (20-day)
    df = df.withColumn("MA_20", avg("Close").over(window_spec.rowsBetween(-19, 0)))

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
    df = df.withColumn("Mean_Return", mean("Daily_Return").over(window_spec.rowsBetween(-19, 0)))
    df = df.withColumn("Std_Dev_Return", stddev("Daily_Return").over(window_spec.rowsBetween(-19, 0)))
    df = df.withColumn("Sharpe_Ratio", col("Mean_Return") / col("Std_Dev_Return"))

    # Save the final dataset to Delta Lake
    df.write.format("delta").mode("overwrite").save(FINAL_DELTA_TABLE_PATH)

    print("✅ Financial metrics computed and saved at", FINAL_DELTA_TABLE_PATH)
    # Confirm the file has been saved
    print(f"✅ Financial metrics saved successfully at {FINAL_DELTA_TABLE_PATH}")