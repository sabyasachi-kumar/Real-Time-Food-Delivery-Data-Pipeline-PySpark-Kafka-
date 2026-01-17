
# **Real-Time Food Delivery Streaming Pipeline**

### **PostgreSQL → Kafka → Spark Structured Streaming → Parquet Data Lake**

---

## **1. Introduction**

In modern food delivery platforms such as Swiggy or Zomato, thousands of customer orders are generated every minute. These systems require continuous real-time ingestion, processing, and storage of transactional data for operational monitoring, delivery performance insights, customer experience analytics, and predictive modelling. Traditional batch-based ETL systems fail to support these requirements, as they introduce latency and lack incremental propagation.

This project implements a fully functional **real-time data engineering pipeline** that ingests raw orders from **PostgreSQL**, streams them through **Apache Kafka**, processes and cleans the data using **Apache Spark Structured Streaming**, and persists them in a **partitioned Parquet Data Lake** designed for analytical workloads. The pipeline guarantees reliable **Change Data Capture (CDC)** behaviour, preventing duplicate ingestion and ensuring deterministic delivery.

The aim is to model an industry-grade streaming architecture demonstrating scalability, fault tolerance, and structured data processing, aligning with enterprise data engineering practices.

---

## **2. Key Objectives**

This project is designed to achieve the following goals:

| Objective               | Description                                                        |
| ----------------------- | ------------------------------------------------------------------ |
| Real-time ingestion     | Capture newly arriving orders without reprocessing historical data |
| Change Data Capture     | Detect only new records using timestamp comparison                 |
| Streaming transport     | Use Kafka as a highly available distributed event broker           |
| Structured processing   | Validate, clean, and enrich streaming records                      |
| Optimized storage layer | Store curated data in Parquet format with date-based partitioning  |
| Fault tolerance         | Use Spark checkpoints and timestamp files for recovery             |
| Parameterized execution | Central YAML config applied across components                      |

---

## **3. End-to-End Architecture**

```
PostgreSQL (Orders Table)
        │
        ▼
Spark CDC Producer (PySpark)
    - Polls DB incrementally
    - Converts rows to JSON
    - Publishes to Kafka topic
        │
        ▼
Kafka Topic: dsai2025em1100189_food_orders_raw
        │
        ▼
Spark Structured Streaming Consumer (PySpark)
    - Reads from Kafka
    - Schema-based parsing
    - Data cleaning & validation
    - Adds partition date column
        │
        ▼
Parquet Data Lake (partitioned by date)
```

### **Rationale for Architecture Choices**

| Component                  | Justification                                                     |
| -------------------------- | ----------------------------------------------------------------- |
| PostgreSQL                 | Realistic transactional OLTP source for food order systems        |
| Kafka                      | Distributed, high-throughput event streaming backbone             |
| Spark Structured Streaming | Scalable continuous processing engine with exactly-once semantics |
| Parquet                    | Columnar storage optimized for analytics and compression          |
| Partitioning               | Enables efficient querying, reduces scan cost                     |

---

## **4. Project Structure**

```
food_delivery_streaming/
└── local/
    ├── db/
    │   └── orders.sql
    ├── producers/
    │   └── orders_cdc_producer.py
    ├── consumers/
    │   └── orders_stream_consumer.py
    ├── configs/
    │   └── orders_stream.yml
    └── scripts/
        ├── producer_spark_submit.sh
        └── consumer_spark_submit.sh
```

This structure reflects a clean modular separation between data ingestion (producer), data processing (consumer), configuration, and deployment scripts.

---

## **5. PostgreSQL Source Table Specification**

| Column          | Type        | Description                     |
| --------------- | ----------- | ------------------------------- |
| order_id        | SERIAL (PK) | Unique order identifier         |
| customer_name   | VARCHAR     | Name of the customer            |
| restaurant_name | VARCHAR     | Restaurant fulfilling the order |
| item            | VARCHAR     | Ordered food item               |
| amount          | NUMERIC     | Monetary price of the order     |
| order_status    | VARCHAR     | Order lifecycle stage           |
| created_at      | TIMESTAMP   | Event timestamp enabling CDC    |

### **Design Consideration**

`created_at` acts as the incremental watermark, enabling the CDC producer to process only new records without rescanning the table.

---

## **6. Configuration Management (`orders_stream.yml`)**

All operational parameters are centrally managed through YAML to ensure portability and minimal code change. It configures:

* Database connection properties
* Kafka topic and broker details
* Data Lake storage directories
* Checkpoint and timestamp locations
* Streaming polling interval

Such external configuration follows industry best practices and supports environment migration (local → staging → production).

---

## **7. Spark CDC Producer – Detailed Processing Logic**

### **Responsibilities**

* Establish a connection to PostgreSQL at each polling interval
* Read complete table snapshot (light-weight for streaming scenarios)
* Filter rows using `created_at > last_processed_timestamp`
* Serialize filtered rows as JSON records
* Publish JSON messages to Kafka topic
* Persist the latest processed timestamp to a local file for future runs

### **Why Timestamp-Based CDC?**

* Prevents reprocessing of previously published rows
* Ensures ordering and incremental progression
* Avoids costly full table diffs or log-based replication

### **Error Handling & Fault Tolerance**

* If producer restarts unexpectedly, processing resumes from the last written timestamp
* Ensures no data loss and no duplication (idempotent design)

---

## **8. Spark Streaming Consumer – Processing and Storage**

### **Responsibilities**

* Continuously consume messages from Kafka in micro-batches
* Decode Kafka's byte payload and parse JSON using a predefined schema
* Apply cleaning rules:

  * Drop records with missing order_id
  * Remove records with negative amounts
* Add `date` column derived from timestamp for partitioning
* Write to Data Lake in **append** mode
* Maintain streaming progress using checkpointing

### **Output Layout**

```
/datalake/food/dsai2025em1100189/output/orders/
    └── date=2025-12-07/
         ├── part-00001.parquet
```

### **Why Parquet + Partitioning**

| Advantage             | Benefit                                  |
| --------------------- | ---------------------------------------- |
| Columnar compression  | Reduced storage size                     |
| Predicate pushdown    | Faster analytical queries                |
| Partition pruning     | Avoids unnecessary file scanning         |
| Data lineage tracking | Each date folder independently queryable |

---

## **9. Execution Instructions**

### Step-by-Step Sequence

| Step | Action                                               |
| ---- | ---------------------------------------------------- |
| 1    | Start Kafka broker                                   |
| 2    | Run CDC Spark Producer *(must be started first)*     |
| 3    | Run Spark Structured Streaming Consumer              |
| 4    | Insert new records into PostgreSQL                   |
| 5    | Verify Parquet files in corresponding date partition |

### Commands

Start Producer:

```bash
bash scripts/producer_spark_submit.sh
```

Start Consumer:

```bash
bash scripts/consumer_spark_submit.sh
```

Insert example event:

```sql
INSERT INTO dsai2025em1100189_orders
(customer_name, restaurant_name, item, amount, order_status, created_at)
VALUES ('Test User', 'Dominos', 'Farmhouse Pizza', 299, 'PLACED', NOW());
```


## **10. Conclusion**

This project demonstrates the construction of a **robust real-time data streaming pipeline** aligned with industry and academic best practices. It incorporates incremental Change Data Capture, distributed event streaming, resilient structured processing, and optimized analytical storage. The design enables scalability, maintainability, and high availability—key attributes required in production environments such as large-scale food delivery networks.

The architecture can be directly extended to predictive order ETA modelling, rider allocation analytics, real-time notification systems, and real-time dashboarding.

---

## **11. Future Enhancements**

* Migration to **Delta Lake** for ACID transactions and time-travel
* **Streaming aggregations** (e.g., revenue per hour, active restaurants)
* **Machine learning** on live streams using Spark ML
* **Kafka Connect** for automated CDC bridging
* Real-time monitoring tools such as **Kafka UI / Grafana / Prometheus**

---
