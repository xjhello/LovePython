#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

import pika

credentials = pika.PlainCredentials("admin","admin")
connection = pika.BlockingConnection(pika.ConnectionParameters('172.31.236.43',credentials=credentials))
channel = connection.channel()

# 声明一个队列(创建一个队列)
channel.queue_declare(queue='ack')
"""

在 no_ack=true 的情况下，RabbitMQ 认为 message 一旦被 deliver出去了，就已被确认了，所以会立即将缓存中的 message 删除。所以在 consumer 异常时会导致消息丢失。
"""
def callback(ch, method, properties, body):
    print("消费者接受到了任务: %r" % body)
    # 通知服务端，消息取走了，如果auto_ack=False，不加下面，消息会一直存在
    sys.exit(1)
    # ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.close()

channel.basic_consume(queue='ack',on_message_callback=callback,auto_ack=False)

channel.start_consuming()