from kafka import KafkaConsumer
from pymongo import MongoClient
import os
from dotenv import load_dotenv, find_dotenv
import json

load_dotenv(find_dotenv())

uri_kafka = os.environ.get('KAFKA_URI')

consumer = KafkaConsumer("pokemon-codes", bootstrap_servers=uri_kafka, auto_offset_reset='earliest', enable_auto_commit=True,
                         auto_commit_interval_ms=1000, group_id="pokemon-codes")


uri = os.environ.get('MONGO_URI')
client = MongoClient(uri)
codes_db = client.codes
collection = codes_db.codes

for code in consumer:
    code_data = json.loads(code.value.decode('utf-8'))
    print(code_data)
    collection.insert_one(code_data)

print(f"two")
consumer.close()
