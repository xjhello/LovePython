#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time

from rabiitmqDemo.GetConnect import get_connect


"""
Direct模式是fanout模式上的一种叠加，增加了路由RoutingKey的模式
"""

channel = get_connect()
# 与routing区别是交换机的类型为 topic
channel.exchange_declare(exchange='routing-topic', exchange_type='topic')

severity = "routing Test"
i = 0
while True:
    message = json.dumps({'OrderId': "1000%s" % i})
    # 向队列插入数值 routing_key是队列名
    channel.basic_publish(exchange='routing-topic', routing_key=severity, body=message)
    print(message)
    time.sleep(1)
    i += 1