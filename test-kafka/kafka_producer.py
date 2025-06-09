from kafka import KafkaProducer
import time

def producer_test():
    producer = KafkaProducer(bootstrap_servers="localhost:9092")

    for _ in range(50):
        producer.send('Test_message', b'Hello World!')

    producer = KafkaProducer(transactional_id='trans_id_12345')
    producer.init_transactions()
    producer.begin_transaction()
    future = producer.send('txn_topic', value=b'working')
    future.get()
    producer.commit_transaction()
    producer.flush()
    producer.close()

if __name__ == "__main__":
    producer_test()