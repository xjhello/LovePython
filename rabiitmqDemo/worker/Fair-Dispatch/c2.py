#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time

from rabiitmqDemo.GetConnect import get_connect

channel = get_connect()

channel.queue_declare(queue="worker-fair", durable=True)

def callback(ch, method, properties, body):
    print("c2接受body:{}".format(body.decode()))
    time.sleep(6)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    # print(body.decode())


# 公平分发 根据消费者的消费能力进行公平分发，处理快的处理的多，处理慢的处理的少；按劳分配
# 与work的轮询不同的地方在于 basic_qos 设置了此条语句 轮询是每个消费者都会有的
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='worker-fair', on_message_callback=callback)

# 开始接收信息，并进入阻塞状态，队列里有信息才会调用callback进行处理
channel.start_consuming()