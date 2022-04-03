#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time

from rabiitmqDemo.GetConnect import get_connect


"""
根据消费者的消费能力进行公平分发，处理快的处理的多，处理慢的处理的少；按劳分配；
"""

channel = get_connect()
# 与简单模式的区别是知道了交换机和交换机的类型为 fanout
channel.exchange_declare(exchange='pu-su', exchange_type='fanout')


i = 0
while True:
    message = json.dumps({'OrderId': "1000%s" % i})
    # 向队列插入数值 routing_key是队列名
    channel.basic_publish(exchange='pu-su', routing_key='', body=message)
    print(message)
    time.sleep(1)
    i += 1