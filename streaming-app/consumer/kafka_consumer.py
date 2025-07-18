from kafka import KafkaConsumer
import json

# Same topics as producer
topics = ["page_loaded", "product_searched", "product_clicked", "warranty_selected", "added_to_cart",
          "product_availability", "product_variant_selected", "cart_viewed", "checking_out"]

consumer = KafkaConsumer(
    *topics,
    bootstrap_servers="kafka:9092",
    api_version=(0, 11, 5),
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