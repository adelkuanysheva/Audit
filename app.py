import swagger_ui_bundle
import connexion
import json
import datetime 
import requests
from connexion import NoContent
import yaml
import logger
import logging.config
import uuid
from pykafka import KafkaClient
from flask_cors import CORS, cross_origin
import os

MAX_EVENTS = 10
EVENT_FILE = 'events.json'

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

logger = logging.getLogger('basicLogger')

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

def ride(index):
    """ Get ride Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving ride at index %d" % index)
    try:
        msg_list = []
        for msg in consumer:
            msg_str = msg.value.decode("utf-8")
            msg = json.loads(msg_str)
            if msg["type"] == "ride":
                msg_list.append(msg["payload"])
        event = [msg_list[index]]
        return event, 200

    except:
        logger.error("No messages found")

    logger.error(f"Could not find ride at index {index}")
    return {"message": "Not Found"}, 404

def heartrate(index):
    """ Get heartrate Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving ride at index %d" % index)
    try:
        msg_list = []
        for msg in consumer:
            msg_str = msg.value.decode("utf-8")
            msg = json.loads(msg_str)
            if msg["type"] == "heartrate":
                msg_list.append(msg["payload"])

        event = [msg_list[index]]
        return event, 200
    except:
        logger.error("No messages found")

    logger.error(f"Could not find heartrate at index {index}")
    return {"message": "Not Found"}, 404


def health():
    logger.info("Health Check returned 200")
    return 200


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
adel = "test"
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)