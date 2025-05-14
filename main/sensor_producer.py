from kafka import KafkaProducer
import json, time, random

producer = KafkaProducer(
  bootstrap_servers=['node1:9092','node2:9092','node3:9092'],
  value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic = "sensor_data"
sensor_ids = ['living_room','bedroom','kitchen','bathroom']
print("Producing sensor readings to Kafka...")

while True:
    sensor_data = {
        "sensor_id": random.choice(sensor_ids),
        "timestamp": int(time.time() * 1000),        # ms
        "temperature": round(random.uniform(15.0, 30.0), 2),
        "water_usage": round(random.uniform(0.0, 10.0), 2),
        "energy_usage": round(random.uniform(0.0, 5.0), 2)
    }
    producer.send(topic, sensor_data)
    print(f"Sent: {sensor_data}")
    time.sleep(1)
