from pyspark.sql import SparkSession
from pyspark.sql.functions import expr
import socket
import time

# Retry until Kafka is up
def wait_for_kafka(broker, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        try:
            host, port = broker.split(":")
            with socket.create_connection((host, int(port)), timeout=5):
                print("Kafka is ready.")
                return
        except:
            print("Waiting for Kafka...")
            time.sleep(5)
    raise Exception("Kafka not available after waiting.")

wait_for_kafka("kafka:9092")

spark = SparkSession.builder \
    .appName("KafkaStructuredStreaming") \
    .getOrCreate()

# Read from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "my-topic") \
    .option("startingOffsets", "latest") \
    .load()

# Assume payloads are JSON strings with an 'event_type'
df_parsed = df.selectExpr("CAST(value AS STRING) as json_str") \
    .selectExpr("from_json(json_str, 'event_type STRING') as data") \
    .select("data.event_type")

# Count event types over a sliding window
agg_df = df_parsed.groupBy("event_type").count()

# Write to custom Flask app
def send_to_flask(batch_df, batch_id):
    metrics = batch_df.toPandas().to_dict("records")
    try:
        requests.post("http://flask-exporter:8000/update_metrics", json=metrics)
    except Exception as e:
        print("Failed to send metrics:", e)

agg_df.writeStream.foreachBatch(send_to_flask).start().awaitTermination()