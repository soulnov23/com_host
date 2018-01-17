#!/usr/bin/python
# -*- coding: UTF-8 -*-

import paho.mqtt.client as mqtt
from pymongo.errors import ConnectionFailure
from pymongo import MongoClient
import socket

def on_connect(client, userdata, flags, rc):
    print("Connection returned result: "+str(rc))
    
def on_disconnect(client, userdata, rc):
    print "on_disconnect"
    
def on_message(client, userdata, message):
     print("Received message '" + str(message.payload) + "' on topic '"
        + message.topic + "' with QoS " + str(message.qos))

def on_publish(client, userdata, mid):
    print "on_publish"
    
def on_subscribe(client, userdata, mid, granted_qos):
    print "on_subscribe"
        
def on_unsubscribe(client, userdata, mid):
    print "on_unsubscribe"
    
if ( __name__ == "__main__"):
    print "main"

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    client.on_unsubscribe = on_unsubscribe
    try:
        print "start"
        client.connect("10.51.23.58", 1883, 60)
        print "end"
        client.loop_start()
    except socket.error, err_msg:
        print err_msg
    print "data"
    result, mid = client.publish("test1", "hello", 0)
    if result == mqtt.MQTT_ERR_SUCCESS:
        print "MQTT_ERR_SUCCESS"
    result, mid = client.publish("test2", "world", 0)
    if result == mqtt.MQTT_ERR_SUCCESS:
        print "MQTT_ERR_SUCCESS"
    result, mid = client.subscribe([("test1", 0), ("test2", 0)])
    if result == mqtt.MQTT_ERR_SUCCESS:
        print "MQTT_ERR_SUCCESS"

    print "start"
    mongo_client = MongoClient(host="10.51.23.58", port=27017, serverSelectionTimeoutMS=1)
    try:
        mongo_client.admin.command("ping")
        #db = mongo_client["default"]
        #col = db["user"]
        #for a in col.find():
        #    print a
    except ConnectionFailure:
        print "connect error"
    print "end"
