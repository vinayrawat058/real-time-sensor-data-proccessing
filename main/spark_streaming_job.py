from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window
from pyspark.sql.types import StructType, StringType, DoubleType, LongType
import psycopg2
from datetime import datetime

# 1. Spark session
spark = SparkSession.builder \
    .appName("SmartHomeIoTStreaming") \
    .getOrCreate()

# 2. Read from Kafka
raw_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers",
            "node1:9092,node2:9092,node3:9092") \
    .option("subscribe", "sensor_data") \
    .option("startingOffsets", "latest") \
    .load()

# 3. Schema includes sensor_id
schema = StructType() \
    .add("sensor_id", StringType(), True) \
    .add("timestamp", LongType(), True) \
    .add("temperature", DoubleType(), True) \
    .add("water_usage", DoubleType(), True) \
    .add("energy_usage", DoubleType(), True)

# 4. Parse JSON, cast timestamp → event_time, watermark
data_df = (
    raw_df
      .select(from_json(col("value").cast("string"), schema).alias("d"))
      .select("d.*")
      .withColumn("event_time", (col("timestamp")/1000).cast("timestamp"))
      .withWatermark("event_time", "1 minute")
)

# 5. Windowed aggregation per sensor
agg_df = data_df.groupBy(
    col("sensor_id"),
    window(col("event_time"), "1 minute", "30 seconds")
).avg("temperature","water_usage","energy_usage")

# 6. Anomaly filter
anomaly_df = data_df.filter(
    (col("temperature") > 28) |
    (col("water_usage") > 9) |
    (col("energy_usage") > 4)
)

# 7. Postgres connection params
DB_PARAMS = {
  "host":     "localhost",
  "port":     5432,
  "database": "iot",
  "user":     "spark_user",
  "password": "ChangeMe!"
}

# 8. Write anomalies into Postgres
def write_anomalies(batch_df, batch_id):
    rows = batch_df.collect()
    if not rows:
        return
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    for r in rows:
        ts = datetime.fromtimestamp(r["timestamp"]/1000.0)
        cur.execute(
          "INSERT INTO anomalies(sensor_id, timestamp, temperature, water_usage, energy_usage) "
          "VALUES (%s,%s,%s,%s,%s)",
          (r["sensor_id"], ts, r["temperature"], r["water_usage"], r["energy_usage"])
        )
    conn.commit()
    cur.close()
    conn.close()

anomaly_query = anomaly_df.writeStream \
    .outputMode("append") \
    .option("checkpointLocation",
            "hdfs://node1:9000/user/pranav/checkpoints/anomalies") \
    .foreachBatch(write_anomalies) \
    .start()

# 9. Write aggregates into Postgres
def write_aggregates(batch_df, batch_id):
    rows = batch_df.collect()
    if not rows:
        return
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    for r in rows:
        sensor = r["sensor_id"]
        start = r["window"].start
        end   = r["window"].end
        avg_t = r["avg(temperature)"]
        avg_w = r["avg(water_usage)"]
        avg_e = r["avg(energy_usage)"]
        cur.execute(
          "INSERT INTO aggregates(sensor_id, window_start, window_end, "
          "avg_temperature, avg_water_usage, avg_energy_usage) "
          "VALUES (%s,%s,%s,%s,%s,%s)",
          (sensor, start, end, avg_t, avg_w, avg_e)
        )
    conn.commit()
    cur.close()
    conn.close()

agg_query_pg = agg_df.writeStream \
    .outputMode("append") \
    .option("checkpointLocation",
            "hdfs://node1:9000/user/pranav/checkpoints/agg_pg") \
    .foreachBatch(write_aggregates) \
    .start()

agg_query = agg_df.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "hdfs://node1:9000/user/pranav/iot_agg") \
    .option("checkpointLocation",
            "hdfs://node1:9000/user/pranav/checkpoints/agg") \
    .start()

spark.streams.awaitAnyTermination()
