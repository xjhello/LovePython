#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pika
# 无密码
# connection = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1'))

# 有密码
credentials = pika.PlainCredentials("admin","admin")
connection = pika.BlockingConnection(pika.ConnectionParameters('172.31.236.43',credentials=credentials))
channel = connection.channel()
# 声明一个队列(创建一个队列)
channel.queue_declare(queue='lqz')

channel.basic_publish(exchange='',
                      routing_key='lqz', # 消息队列名称
                      body='hello world')
connection.close()