#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import pika
import json


def get_connect():
    credentials = pika.PlainCredentials('admin', 'admin')  # mq用户名和密码
    # 虚拟队列需要指定参数 virtual_host，如果是默认的可以不填。
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='172.31.236.43', port=5672, virtual_host='/', credentials=credentials))
    channel = connection.channel()
    return channel