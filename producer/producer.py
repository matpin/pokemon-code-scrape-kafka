from kafka import KafkaProducer
from scraper import scrape_page
import json
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

uri_kafka = os.environ.get('KAFKA_URI')

producer = KafkaProducer(bootstrap_servers=uri_kafka)

topic = "pokemon-codes"

scraped_data = scrape_page()


if scraped_data:
    for code in scraped_data:
        code_json = json.dumps(code)
        code_bytes = code_json.encode('utf-8')
        producer.send(topic, code_bytes)

producer.close()
