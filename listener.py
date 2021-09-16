import boto3
import pymongo
import paho.mqtt.client as mqtt 

from urllib.parse import urlparse
from datetime import datetime, date
from json import dumps, loads
from random import randrange, randint, uniform
from time import time

# Constants
LOGPREFIX = "myHealth"
TOPIC = 'vitalsign'

def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))
    
def on_message(client, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    
def on_publish(client, obj, mid):
    print("obj: " + str(obj))
    print("mid: " + str(mid))
    
def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))
    print("obj: " + str(obj))
    
def on_log(client, obj, level, string):
    print(string)

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
    
    # # Start subscribe, with QoS level 0
    # mqttc.subscribe(TOPIC, 0)
     
    # # Continue the network loop, exit when an error occurs
    # rc = 0
    # while rc == 0:
    #     rc = mqttc.loop()
    # print("rc: " + str(rc))
    
def get_parameter_value(key):
    print("{} - Get Parameter key: {}".format(LOGPREFIX, key))
    ssm_client = boto3.client("ssm")
    value = ssm_client.get_parameter(Name=key, WithDecryption=False)
    return value.get("Parameter").get("Value")

if __name__ == "__main__":
    print("HELLO WORLD")
    main()