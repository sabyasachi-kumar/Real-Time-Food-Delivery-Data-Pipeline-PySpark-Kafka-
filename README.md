# Real-Time Change Data Capture (CDC) Pipeline for Food Delivery Orders

## Abstract

This project implements an end-to-end real-time Change Data Capture (CDC) pipeline using Apache Spark, Apache Kafka, and PostgreSQL. The system incrementally captures newly inserted records from a transactional PostgreSQL database, streams them through Kafka in JSON format, and processes them using Spark Structured Streaming before persisting the cleaned and transformed data into a partitioned Parquet-based data lake. The pipeline is designed to be fault-tolerant, configurable, and scalable, closely resembling real-world data engineering architectures used in production systems.

---

## 1. Introduction

Modern data-driven applications require near real-time ingestion and processing of transactional data for analytics, reporting, and downstream machine learning workflows. Change Data Capture (CDC) enables such systems by tracking and propagating changes from source databases to streaming platforms and data lakes.

This project demonstrates a timestamp-based CDC approach implemented using Apache Spark, without relying on log-based tools such as Debezium. It focuses on clarity, modularity, and configurability, making it suitable for academic study and practical learning.

---

## 2. System Architecture

The overall architecture of the pipeline is as follows:

PostgreSQL (Orders Table)  
→ Spark CDC Producer (JDBC-based polling)  
→ Apache Kafka (JSON event stream)  
→ Spark Structured Streaming Consumer  
→ Parquet Data Lake (Date-partitioned)

The producer and consumer are decoupled using Kafka, enabling scalable and fault-tolerant stream processing.

---

## 3. Technology Stack

- Apache Spark 3.5.1
- Apache Kafka
- PostgreSQL
- PySpark
- Parquet
- YAML for configuration management

---

## 4. Project Structure

```

food_delivery_streaming/
│
├── producers/
│   └── orders_cdc_producer.py
│
├── consumers/
│   └── orders_stream_consumer.py
│
├── configs/
│   └── orders_stream.yml
│
├── scripts/
│   ├── producer_spark_submit.sh
│   └── consumer_spark_submit.sh
│
└── datalake/
└── orders/

````

---

## 5. Configuration Management

All system configurations are externalized in a YAML file to ensure separation of code and environment-specific parameters.

Example configuration:

```yaml
postgres:
  jdbc_url: jdbc:postgresql://localhost:5432/food_db
  table: orders
  user: postgres
  password: postgres

kafka:
  brokers: localhost:9092
  topic: orders_cdc

datalake:
  path: ./datalake/orders
  format: parquet

streaming:
  batch_interval: 10
  checkpoint_location: ./checkpoints/orders
  last_processed_timestamp_location: ./state/last_ts.txt
````

---

## 6. CDC Producer Design (PostgreSQL to Kafka)

The CDC producer is implemented using Apache Spark in batch mode with periodic execution.

Key responsibilities:

* Connects to PostgreSQL using JDBC
* Reads the orders table
* Filters records based on the `created_at` timestamp to capture only new rows
* Serializes records into JSON format
* Publishes messages to a Kafka topic
* Maintains state by persisting the last processed timestamp

This design ensures idempotency and fault tolerance across restarts.

Relevant file:

* `orders_cdc_producer.py`

---

## 7. Streaming Consumer Design (Kafka to Data Lake)

The streaming consumer uses Spark Structured Streaming to process Kafka events continuously.

Key responsibilities:

* Subscribes to the Kafka topic
* Parses JSON messages using an explicitly defined schema
* Applies data quality checks such as null validation and non-negative amount filtering
* Adds a derived date column for partitioning
* Writes the processed data to a Parquet-based data lake
* Uses checkpointing to guarantee exactly-once semantics

Relevant file:

* `orders_stream_consumer.py`

---

## 8. Execution Instructions

### 8.1 Prerequisites

* Running PostgreSQL instance with an orders table
* Running Apache Kafka broker
* Apache Spark installed locally
* Python environment with PySpark support

### 8.2 Running the CDC Producer

```bash
bash producer_spark_submit.sh
```

### 8.3 Running the Streaming Consumer

```bash
bash consumer_spark_submit.sh
```

---

## 9. Output Data Format

The final output is stored in Parquet format and partitioned by date to enable efficient analytical queries.

Example output structure:

```
datalake/orders/
└── date=YYYY-MM-DD/
    └── part-00000.snappy.parquet
```

---

## 10. Fault Tolerance and Reliability

* Kafka ensures durable message storage and decoupling between producer and consumer
* Spark checkpoints enable recovery from failures without data loss
* Persistent timestamp tracking prevents duplicate ingestion

