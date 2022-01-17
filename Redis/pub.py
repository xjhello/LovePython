#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/21 4:42 下午
# @Author  : Xujian
import redis

number_list = ['300033', '300032', '300031', '300030']
signal = ['1', '-1', '1', '-1']

rc = redis.StrictRedis(host='127.0.0.1', port='6379', db=3)
for i in range(len(number_list)):
    value_new = str(number_list[i]) + ' ' + str(signal[i])
    rc.publish("liao:1", value_new)  # 发布消息到liao

class A():
    def a(self):
        print(1111)
    def a(self, a,b):
        print(1)
A().a()

