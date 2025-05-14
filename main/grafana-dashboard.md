

## Grafana Dashboards

Five panels and their SQL queries:

1. **Temperature Trend**

   ```sql
   SELECT
     $__time(window_start) AS time,
     avg_temperature AS value,
     sensor_id AS metric
   FROM aggregates
   WHERE $__timeFilter(window_start)
   ORDER BY time ASC;
   ```

2. **Water Usage Trend**

   ```sql
   SELECT
     $__time(window_start) AS time,
     avg_water_usage AS value,
     sensor_id AS metric
   FROM aggregates
   WHERE $__timeFilter(window_start)
   ORDER BY time ASC;
   ```

3. **Energy Consumption Trend**

   ```sql
   SELECT
     $__time(window_start) AS time,
     avg_energy_usage AS value,
     sensor_id AS metric
   FROM aggregates
   WHERE $__timeFilter(window_start)
   ORDER BY time ASC;
   ```

4. **Recent Anomalies Table**

   ```sql
   SELECT
     $__time(timestamp) AS time,
     sensor_id,
     temperature,
     water_usage,
     energy_usage
   FROM anomalies
   WHERE $__timeFilter(timestamp)
   ORDER BY time DESC
   LIMIT 50;
   ```

5. **Anomaly Count per Minute**

   ```sql
   SELECT
     $__timeGroupAlias(timestamp,'1m') AS time,
     COUNT(*) AS anomaly_count
   FROM anomalies
   WHERE $__timeFilter(timestamp)
   GROUP BY time
   ORDER BY time ASC;
   ```

