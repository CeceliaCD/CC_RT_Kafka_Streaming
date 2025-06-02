from kafka import KafkaConsumer
import json
from utils.yaml_loader import yaml_kafka_host_loader

producer_host = yaml_kafka_host_loader('../docker-compose.yaml')

# Same topics as producer
topics = ["page_loaded", "product_searched", "product_clicked", "warranty_selected", "added_to_cart",
          "product_availability", "product_variant_selected", "cart_viewed", "checking_out"]

# Create Kafka consumer
consumer = KafkaConsumer(
    *topics,
    bootstrap_servers=producer_host,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',  # or 'latest'
    enable_auto_commit=True,
    group_id='amazon-shopping-consumer-group'
)

print("Listening for events...\n")

for message in consumer:
    topic = message.topic
    event = message.value

    print(f"\n--- Event from topic: {topic} ---")
    print(f"Shopping_Timestamp    : {event.get('shopping_timestamp')}")
    print(f"Action_Type  : {event.get('action_type')}")
    print(f"Target       : {event.get('target')}")
    print(f"Value        : {event.get('value')}")
    print(f"URL          : {event.get('url')}")