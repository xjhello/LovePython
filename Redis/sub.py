#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/21 4:43 下午
# @Author  : Xujian
import time
import redis

rc = redis.StrictRedis(host='127.0.0.1', port='6379', db=3)
ps = rc.pubsub()
ps.subscribe('liao:1')  # 从liao订阅消息
print(111111)
for item in ps.listen():  # 监听状态：有消息发布了就拿过来
    if item['type'] == 'message':
        print (item['channel'])
        print (item['data'])
# while True:
#     msg = ps.listen()
#     print(msg)