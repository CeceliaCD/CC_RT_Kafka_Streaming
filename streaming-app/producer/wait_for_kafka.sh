#!bin/bash

KAFKA_HOST=kafka
KAFKA_PORT=9092

echo "Waiting for Kafka to be available at $KAFKA_HOST:$KAFKA_PORT.."

until nc -z $KAFKA_HOST $KAFKA_PORT; do
  echo "$(date + "%Y-%m-%d %H-%M-%S") Kafka is not available yet. Sleeping..."
  sleep 2
done

echo "Kafka is up! Starting the producer..."
exec python3 amazon_shopping_transaction_producer.py