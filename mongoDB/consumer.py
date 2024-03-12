from kafka import KafkaConsumer
from pymongo import MongoClient
import os
from dotenv import load_dotenv, find_dotenv
import json
from kafka import KafkaProducer
import fastavro
from fastavro.schema import load_schema
from fastavro import validate

load_dotenv(find_dotenv())

uri_kafka = os.environ.get('KAFKA_URI')

consumer = KafkaConsumer("pokemon-codes", bootstrap_servers=uri_kafka, auto_offset_reset='earliest', enable_auto_commit=True,
                         auto_commit_interval_ms=1000, group_id="pokemon-codes")

dlq = "dead-letter-queue"
producer = KafkaProducer(bootstrap_servers=uri_kafka)

avro_schema = load_schema("./schema_validation.avsc")

uri = os.environ.get('MONGO_URI')
client = MongoClient(uri)
codes_db = client.codes
collection = codes_db.codes


for code in consumer:
    try:
        code_data = json.loads(code.value.decode('utf-8'))
        validate(code_data, avro_schema)
        collection.insert_one(code_data)
    except fastavro.schema.SchemaParseException as e:
        producer.send(dlq, value=code.value)
        print("Validation failed. Invalid Avro schema.")
        print("Sent to dead-letter queue:", code.value)
    except Exception as e:
        producer.send(dlq, value=code.value)
        print("An error occurred:", e)
        print("Sent to dead-letter queue:", code.value)

consumer.close()
