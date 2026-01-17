import argparse
import yaml
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_date
from pyspark.sql.types import (StructType, StructField,
                               IntegerType, StringType, DoubleType, TimestampType)

# Load config
def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_config(args.config)

    kafka_cfg = config["kafka"]
    datalake_cfg = config["datalake"]
    stream_cfg = config["streaming"]

    # Create Spark Session
    spark = (
        SparkSession.builder
        .appName("OrdersStreamConsumer")
        .config("spark.jars.packages",
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1")
        .getOrCreate()
    )

    # Define JSON schema
    order_schema = StructType([
        StructField("order_id", IntegerType(), True),
        StructField("customer_name", StringType(), True),
        StructField("restaurant_name", StringType(), True),
        StructField("item", StringType(), True),
        StructField("amount", DoubleType(), True),
        StructField("order_status", StringType(), True),
        StructField("created_at", TimestampType(), True)
    ])

    # Read from Kafka as streaming source
    raw_df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", kafka_cfg["brokers"])
        .option("subscribe", kafka_cfg["topic"])
        .option("startingOffsets", "earliest")
        .load()
    )

    # Convert binary to string JSON
    json_df = raw_df.selectExpr("CAST(value AS STRING) as json_str")

    # Parse JSON into columns
    parsed_df = json_df.select(
        from_json(col("json_str"), order_schema).alias("data")
    ).select("data.*")

    # Clean data (business logic filters)
    cleaned_df = parsed_df.filter(
        col("order_id").isNotNull() &
        (col("amount") >= 0)
    )

    # Add date partition column
    final_df = cleaned_df.withColumn("date", to_date(col("created_at")))

    # Write to Data Lake in Parquet format
    query = (
        final_df.writeStream
        .format(datalake_cfg["format"])  # parquet
        .option("path", datalake_cfg["path"])
        .option("checkpointLocation", stream_cfg["checkpoint_location"])
        .partitionBy("date")
        .outputMode("append")
        .start()
    )

    query.awaitTermination()
