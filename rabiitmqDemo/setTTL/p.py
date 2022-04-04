#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pika
from pika.adapters.blocking_connection import BlockingChannel

credentials = pika.PlainCredentials("root", "123")

conn = pika.BlockingConnection(pika.ConnectionParameters(host='10.211.55.20', credentials=credentials))
# 超时时间
conn.add_timeout(5, lambda: channel.stop_consuming())

channel = conn.channel()

channel.queue_declare(queue='hello')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    channel.stop_consuming()


channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

# 设置超时时间