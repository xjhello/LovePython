#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time

from rabiitmqDemo.GetConnect import get_connect

channel = get_connect()

channel.queue_declare(queue="worker-fair", durable=True)

def callback(ch, method, properties, body):
    print("c1接受body:{}".format(body.decode()))
    time.sleep(1)
    ch.basic_ack(delivery_tag=method.delivery_tag)



# 公平分发 如果该消费者的channel上未确认的消息数达到了prefetch_count数，则不向该消费者发送消息
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='worker-fair', on_message_callback=callback)

# 开始接收信息，并进入阻塞状态，队列里有信息才会调用callback进行处理
channel.start_consuming()