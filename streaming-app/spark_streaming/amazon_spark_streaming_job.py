from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, TimestampType, StructType, StructField
from pyspark.sql.functions import from_json, col, window
import requests
import os
from dotenv import load_dotenv
import socket
import time

load_dotenv()

# Retrying until Kafka is up
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

event_schema = StructType([
    StructField("shopping_timestamp", TimestampType()),
    StructField("action_type", StringType()),
    StructField("target", StringType()),
    StructField("value", StringType()),
    StructField("url", StringType())
])

spark = SparkSession.builder \
    .appName("KafkaStructuredStreamingforAmazonShopping") \
    .getOrCreate()

# Reading from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "page_loaded,product_searched,product_clicked,warranty_selected,added_to_cart,product_availability,product_variant_selected,cart_viewed,checking_out") \
    .option("startingOffsets", "latest") \
    .load()

# Payloads are JSON strings with an event_schema and unpacking the schema
df_parsed = df.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), event_schema).alias("amazon_shopping_data")) \
    .select("amazon_shopping_data.*")

agg_df = df_parsed.groupBy(window("shopping_timestamp", "1 minute"),
                           "action_type").count()

mongo_un = os.getenv("MONGODB_USERNAME")
mongo_pw = os.getenv("MONGODB_PASSWORD")
kafka_db = os.getenv("KAFKA_STREAMING_DB")
kafka_coll = os.getenv("AMAZON_COLLECTION")

agg_df.writeStream \
    .format("mongo") \
    .option("spark.mongodb.connection.uri", f"mongodb+srv://{mongo_un}:{mongo_pw}@ccdcluster2025.oon2fh6.mongodb.net/") \
    .option("spark.mongodb.write.connection.uri", f"mongodb+srv://{mongo_un}:{mongo_pw}@ccdcluster2025.oon2fh6.mongodb.net/") \
    .option("spark.mongodb.database", kafka_db) \
    .option("spark.mongodb.collection", kafka_coll) \
    .option("checkpointLocation", "/tmp/mongo_checkpoint") \
    .start() \
    .awaitTermination()

def send_to_flask(batch_df, batch_id):
    metrics = batch_df.toPandas().to_dict("records")
    try:
        requests.post("http://flask-exporter:8000/update_metrics", json=metrics)
    except Exception as e:
        print("Failed to send metrics:", e)

agg_df.writeStream.foreachBatch(send_to_flask).start().awaitTermination()

