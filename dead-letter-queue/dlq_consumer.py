from kafka import KafkaConsumer
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

uri_kafka = os.environ.get('KAFKA_URI')

consumer = KafkaConsumer("dead-letter-queue", bootstrap_servers=uri_kafka, auto_offset_reset='earliest', enable_auto_commit=True,
                         auto_commit_interval_ms=1000, group_id="dlq")

for message in consumer:
    print("Error:", message)

consumer.close()
