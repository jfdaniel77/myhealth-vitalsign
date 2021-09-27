import boto3
import pymongo
import paho.mqtt.client as mqtt 

from urllib.parse import urlparse
from datetime import datetime, date
from json import dumps, loads
from random import randrange, randint, uniform
from time import time
from botocore.config import Config

my_config = Config(
    region_name = 'ap-southeast-1',
    signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

# Constants
LOGPREFIX = "myHealth"
TOPIC = 'vitalsign'

def on_connect(client, userdata, flags, rc):
    print("{} - On Connect - client: {}".format(LOGPREFIX, client))
    print("{} - On Connect - userdata: {}".format(LOGPREFIX, userdata))
    print("{} - On Connect - flags: {}".format(LOGPREFIX, flags))
    print("{} - On Connect - rc: {}".format(LOGPREFIX, rc))
    
def on_message(client, obj, msg):
    print("{} - On Message - client: {}".format(LOGPREFIX, client))
    print("{} - On Message - obj: {}".format(LOGPREFIX, obj))
    print("{} - On Message - msg topic: {}".format(LOGPREFIX, msg.topic))
    print("{} - On Message - msg qos: {}".format(LOGPREFIX, msg.qos))
    print("{} - On Message - msg payload: {}".format(LOGPREFIX, msg.payload))
    store_data(msg.payload)
    
    if datetime.now().minute < 10:
        send_data_to_queue(msg.payload)
    
def on_publish(client, obj, mid):
    print("{} - On Publish - client: {}".format(LOGPREFIX, client))
    print("{} - On Publish - obj: {}".format(LOGPREFIX, obj))
    print("{} - On Publish - mid: {}".format(LOGPREFIX, mid))
    
def on_subscribe(client, obj, mid, granted_qos):
    print("{} - On Subscribe - client: {}".format(LOGPREFIX, client))
    print("{} - On Subscribe - obj: {}".format(LOGPREFIX, obj))
    print("{} - On Subscribe - mid: {}".format(LOGPREFIX, mid))
    print("{} - On Subscribe - granted_qos: {}".format(LOGPREFIX, granted_qos))
    
def on_log(client, obj, level, string):
    print("{} - On Log - client: {}".format(LOGPREFIX, client))
    print("{} - On Log - obj: {}".format(LOGPREFIX, obj))
    print("{} - On Log - level: {}".format(LOGPREFIX, level))
    print("{} - On Log - string: {}".format(LOGPREFIX, string))

mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

def main():
    # Connect
    url_str = get_parameter_value("serverless-mqtt-url")
    url = urlparse(url_str)
    mqttc.username_pw_set(get_parameter_value("serverless-mqtt-user"), get_parameter_value("serverless-mqtt-pwd"))
    
    mqttc.connect(url.hostname, url.port)
    print("{} - Connection has been established.".format(LOGPREFIX))
    
    # # Start subscribe, with QoS level 0
    mqttc.subscribe(TOPIC, 0)
    print("{} - This service has subscribed to mqtt topic.".format(LOGPREFIX))
    
    # Continue the network loop, exit when an error occurs
    print("{} - Start to consume.".format(LOGPREFIX))
    rc = 0
    while rc == 0:
        rc = mqttc.loop()
        print("rc: " + str(rc))
    
def get_parameter_value(key):
    print("{} - Get Parameter key: {}".format(LOGPREFIX, key))
    ssm_client = boto3.client("ssm", config=my_config)
    value = ssm_client.get_parameter(Name=key, WithDecryption=False)
    return value.get("Parameter").get("Value")
    
def store_data(payload):
    print("{} - Store Data to MongoDB".format(LOGPREFIX))
    
    response_payload = {}
    
    mongodb_url = get_parameter_value('serverless-mongodb-url')
    mdb_client = pymongo.MongoClient(mongodb_url)
    db = mdb_client['myhealth']
    vitalsign = db['vitalsign']
    vitalsign_id = vitalsign.insert_one(loads(payload))
    return None
    
def send_data_to_queue(payload):
    print("{} - Send Data to SQS Queue".format(LOGPREFIX))
    
    queue_url = get_parameter_value('serverless-alert-queue-url')
    client = boto3.client('sqs')
    response = client.send_message(QueueUrl=queue_url, MessageBody=payload)
    print("{} - Payload has been pushed to SQS".format(LOGPREFIX))

if __name__ == "__main__":
    print("Listener to mqtt channel is starting...")
    main()