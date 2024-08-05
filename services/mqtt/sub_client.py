#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A small example subscriber
"""
import paho.mqtt.client as paho

def on_message(mosq, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    mosq.publish('pong', 'ack', 0)

def on_publish(mosq, obj, mid):
    pass

if __name__ == '__main__':
    client = paho.Client()
    client.on_message = on_message
    client.on_publish = on_publish

    # Set MQTT broker username and password
    client.username_pw_set(username="thuhuong", password="thuhuong")

    # Connect to the MQTT broker
    client.connect("51.79.251.117", 8885, 60)

    # Subscribe to topics
    client.subscribe("hub/lights", 0)
    client.subscribe("hub/switches", 0)

    # Keep the client loop running
    while client.loop() == 0:
        pass
