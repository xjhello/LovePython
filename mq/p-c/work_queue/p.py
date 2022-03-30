#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time

import pika
import sys

# connection = pika.BlockingConnection(
#     pika.ConnectionParameters(host='localhost'))
# channel = connection.channel()

credentials = pika.PlainCredentials('admin', 'admin')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='172.31.236.43', port=5672, virtual_host='/', credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)

# message = ' '.join(sys.argv[1:]) or "Hello World!"
i=0
while True:
    i+=1
    message = json.dumps({'OrderId': "1000%s" % i})
    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    print(" [x] Sent %r" % message)
    time.sleep(2)

connection.close()