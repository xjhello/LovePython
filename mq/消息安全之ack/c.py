#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pika

credentials = pika.PlainCredentials("admin","admin")
connection = pika.BlockingConnection(pika.ConnectionParameters('172.31.236.43',credentials=credentials))
channel = connection.channel()

# 声明一个队列(创建一个队列)
channel.queue_declare(queue='lqz')

def callback(ch, method, properties, body):
    print("消费者接受到了任务: %r" % body)
    # 通知服务端，消息取走了，如果auto_ack=False，不加下面，消息会一直存在
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='lqz',on_message_callback=callback,auto_ack=False)

channel.start_consuming()