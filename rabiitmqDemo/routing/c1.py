#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time

from rabiitmqDemo.GetConnect import get_connect

channel = get_connect()

channel.exchange_declare(exchange='routing-test', exchange_type='direct')

# 创建一个queue
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
print("创建的queue名称：{}".format(queue_name))
# 绑定到交换机上

severity = "routing Test"
channel.queue_bind(exchange='routing-test', queue=queue_name, routing_key=severity)


def callback(ch, method, properties, body):
    print("c1  订阅 {} 的 body:{}".format("pu-su", body.decode()))
    # time.sleep(1)
    # ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

# 开始接收信息，并进入阻塞状态，队列里有信息才会调用callback进行处理
channel.start_consuming()