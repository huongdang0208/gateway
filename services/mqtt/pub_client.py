#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
Publish some messages to queue
"""
import paho.mqtt.publish as publish


msgs = [{'topic': "hub/lights", 'payload': "01"},
        {'topic': "hub/switches", 'payload': ""},
        {'topic': "adult/news", 'payload': "extra extra"},
        {'topic': "adult/news", 'payload': "super extra"}]

host = "51.79.251.117"
port = 8885

def publish_single_message(topic, message):
    print(message)
    publish.single(topic=topic, payload=message, hostname=host, port=port, auth={'username': 'thuhuong', 'password': 'thuhuong'})

def publish_multiple_messages(msgs):
    publish.multiple(msgs, hostname=host)

