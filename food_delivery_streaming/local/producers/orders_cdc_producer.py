import argparse
import time
import yaml
import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_json, struct, max as spark_max

# Load YAML config file
def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

# Read last processed timestamp
def read_last_timestamp(path):
    if not os.path.exists(path):
        return "1970-01-01 00:00:00"  # default for first run
    with open(path, "r") as f:
        return f.read().strip()

# Write updated timestamp
def write_last_timestamp(path, ts_str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(ts_str)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_config(args.config)

    postgres_cfg = config["postgres"]
    kafka_cfg = config["kafka"]
    stream_cfg = config["streaming"]

    # Spark Session
    spark = (
        SparkSession.builder
        .appName("OrdersCDCProducer")
        .config("spark.jars.packages",
                "org.postgresql:postgresql:42.7.3,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1")
        .getOrCreate()
    )

    jdbc_url = postgres_cfg["jdbc_url"]
    table = postgres_cfg["table"]
    user = postgres_cfg["user"]
    password = postgres_cfg["password"]

    last_ts_path = stream_cfg["last_processed_timestamp_location"]
    batch_interval = int(stream_cfg["batch_interval"])

    print("\n===== CDC Producer Started =====")

    while True:
        last_ts = read_last_timestamp(last_ts_path)
        print(f"Last processed timestamp: {last_ts}")

        # Read table
        df = (
            spark.read.format("jdbc")
            .option("url", jdbc_url)
            .option("dbtable", table)
            .option("user", user)
            .option("password", password)
            .option("driver", "org.postgresql.Driver")
            .load()
        )

        # Filter only new rows
        new_rows = df.filter(col("created_at") > last_ts)

        if new_rows.count() > 0:
            print(f"New rows detected: {new_rows.count()}")

            # Convert to JSON format required by Kafka
            json_df = new_rows.select(
                to_json(struct(
                    "order_id",
                    "customer_name",
                    "restaurant_name",
                    "item",
                    "amount",
                    "order_status",
                    "created_at"
                )).alias("value")
            )

            # Write to Kafka
            (
                json_df.write
                .format("kafka")
                .option("kafka.bootstrap.servers", kafka_cfg["brokers"])
                .option("topic", kafka_cfg["topic"])
                .save()
            )

            # Update last processed timestamp
            max_ts = new_rows.select(spark_max("created_at")).collect()[0][0]
            write_last_timestamp(last_ts_path, str(max_ts))

            print(f"Updated last timestamp to: {max_ts}")

        else:
            print("No new rows found.")

        time.sleep(batch_interval)
