#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import pika
import json

credentials = pika.PlainCredentials('admin', 'admin')  # mq用户名和密码
# 虚拟队列需要指定参数 virtual_host，如果是默认的可以不填。
connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.31.236.43', port=5672, virtual_host='/', credentials=credentials))
channel = connection.channel()

"""
  queue, 队列名称
  passive=False,  
  durable=False,  是否持久化
  exclusive=False,  排他性，是否独立独占  
  auto_delete=False,  是否自动删除  
  arguments=None  携带附属参数
"""
channel.queue_declare(queue='simple-test')
# 开启发布确认！
channel.confirm_delivery()
# 单个确认发布

# 异步确认发布


i = 0
while True:
    message = json.dumps({'OrderId': "1000%s" % i})
    # 向队列插入数值 routing_key是队列名
    channel.basic_publish(exchange='', routing_key='simple-test', body=message)
    print(message)
    print(channel._basic_consume_ok_result)
    time.sleep(1)
    i += 1


# for i in range(10):
#     message=json.dumps({'OrderId':"1000%s"%i})
# # 向队列插入数值 routing_key是队列名
#     channel.basic_publish(exchange = '',routing_key = 'python-test',body = message)
#     print(message)
# connection.close()
