#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time

from rabiitmqDemo.GetConnect import get_connect

channel = get_connect()

channel.queue_declare(queue="worker-round", durable=True)

def callback(ch, method, properties, body):
    print("c2轮询接受body:{}".format(body.decode()))
    time.sleep(6)
    exit(1)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    # print(body.decode())


channel.basic_consume(queue='worker-round', on_message_callback=callback)

# 开始接收信息，并进入阻塞状态，队列里有信息才会调用callback进行处理
channel.start_consuming()