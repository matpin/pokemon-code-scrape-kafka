from kafka import KafkaConsumer
from discord_webhook import DiscordWebhook, DiscordEmbed
from dotenv import load_dotenv, find_dotenv
import os
import json
from kafka import KafkaProducer
import fastavro
from fastavro.schema import load_schema
from fastavro import validate

load_dotenv(find_dotenv())

uri_kafka = os.environ.get('KAFKA_URI')

consumer = KafkaConsumer("pokemon-codes", bootstrap_servers=uri_kafka, auto_offset_reset='earliest', enable_auto_commit=True,
                         auto_commit_interval_ms=1000, group_id="pokemon-codes-webhook")

dlq = "dead-letter-queue"
producer = KafkaProducer(bootstrap_servers=uri_kafka)

avro_schema = load_schema("./schema_validation.avsc")

webhook_url = os.environ.get('WEBHOOK_URL')


for code in consumer:
    try:
        code_data = json.loads(code.value.decode('utf-8'))
        validate(code_data, avro_schema)
        webhook = DiscordWebhook(url=webhook_url)
        embed = DiscordEmbed(title="New codes", color=0xFFFF00)
        embed.set_author(name="Pokemon Scarlet & Violet Gift Codes", url="https://www.nintendolife.com/guides/pokemon-scarlet-and-violet-mystery-gift-codes-list", icon_url="https://oyster.ignimgs.com/mediawiki/apis.ign.com/pokemon-blue-version/8/89/Pikachu.jpg")
        embed.set_thumbnail(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/International_Pok%C3%A9mon_logo.svg/1200px-International_Pok%C3%A9mon_logo.svg.png")
        embed.add_embed_field(name=f':video_game: Code: {code_data["code"]}',
                              value=f':gift: Gift: {code_data["gift"]}\n :hourglass: Expires on: {code_data["expire_date"]}',
                              inline=False)

        webhook.add_embed(embed)
        webhook.execute()
    except fastavro.schema.SchemaParseException as e:
        producer.send(dlq, value=code.value)
        print("Validation failed. Invalid Avro schema.")
        print("Sent to dead-letter queue:", code.value)
    except Exception as e:
        producer.send(dlq, value=code.value)
        print("An error occurred:", e)
        print("Sent to dead-letter queue:", code.value)


consumer.close()
