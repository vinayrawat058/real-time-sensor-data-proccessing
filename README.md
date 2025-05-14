# Real-Time Smart Home Analytics Pipeline

This project implements a cloud-native, real-time analytics pipeline for smart home IoT sensor data using open-source technologies. 

## Features

* **Data Ingestion:** High-throughput messaging with Apache Kafka (multi-broker).
* **Stream Processing:** Apache Spark Structured Streaming with windowed aggregations and anomaly detection.
* **Storage:**

  * **Hot:** PostgreSQL for time-series analytics and Grafana dashboards.
  * **Cold:** Hadoop HDFS with Parquet archives.
* **Visualization:** Grafana dashboards (auto-refresh).
* **Fault Tolerance:** Checkpointing in HDFS and Kafka replication for zero data loss.

## Repository Structure

```
├── sensor_producer.py       # Kafka producer simulating IoT sensors
├── spark_streaming_job.py   # Spark Structured Streaming job
├── README.md                # This file
└── docs/                    # report
```

## Prerequisites

* **Local PoC:** macOS or Ubuntu, Java 11, Python 3, Hadoop, Kafka, Spark, PostgreSQL, Grafana.
* **Cloud Cluster:** Three Ubuntu 22.04 VMs on Jetstream.

## Local Setup

1. **Install dependencies** (macOS brew / apt): Java, Python3, Hadoop, Kafka, Spark, PostgreSQL, Grafana.
2. **Configure Hadoop** (single-node): format HDFS, start DFS & YARN.
3. **Start ZooKeeper & Kafka**: `zookeeper-server-start.sh`, then `kafka-server-start.sh`.
4. **Create Kafka topic**:

   ```bash
   kafka-topics.sh --create --topic sensor_data --bootstrap-server localhost:9092 \
     --partitions 3 --replication-factor 3
   ```
5. **Start PostgreSQL**, create `iot` DB, tables `anomalies`, `aggregates`.
6. **Run Producer**:

   ```bash
   python3 sensor_producer.py
   ```
7. **Submit Streaming Job**:

   ```bash
   spark-submit --master local[*] --packages \
     org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 spark_streaming_job.py
   ```
8. **Install & configure Grafana**, add PostgreSQL data source, import dashboards.

## Cloud Deployment (Jetstream)

Follow the step-by-step guide in the report or docs:

1. Provision 3 VMs (node1, node2, node3).
2. Install & configure Hadoop, Kafka, Spark, PostgreSQL, Grafana across nodes.
3. Run sensor_producer on master node.
4. Submit Spark job to YARN on master node.
5. Access Grafana at `http://<node1_ip>:3000`.

## Grafana Dashboards

Six panels:

1. Temperature Trend
2. Water Usage Trend
3. Energy Consumption Trend
4. Recent Anomalies Table
5. Anomaly Count per Minute
