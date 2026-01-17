# Food Delivery Orders – Real-Time CDC Streaming Pipeline

An end-to-end **Change Data Capture (CDC)** streaming pipeline built using **Apache Spark**, **Apache Kafka**, and **PostgreSQL**.  
This project demonstrates how new records from a transactional database can be incrementally captured, streamed, processed, and stored in a data lake in near real-time.

---

##  Architecture Overview

PostgreSQL (Orders Table)
        
Spark CDC Producer (Batch Polling)
        
Kafka Topic (JSON Events)
        
Spark Structured Streaming Consumer
        
Parquet Data Lake (Partitioned by Date)


## Features

- Incremental CDC using timestamp-based polling
- Kafka-based event streaming
- Schema-enforced JSON parsing
- Data quality validation
- Partitioned Parquet data lake storage
- Fault tolerance via checkpoints
- Externalized configuration using YAML


## Tech Stack

- **Apache Spark 3.5.1**
- **Apache Kafka**
- **PostgreSQL**
- **PySpark**
- **Parquet**
- **YAML Configuration**

---

## 📂 Project Structure

