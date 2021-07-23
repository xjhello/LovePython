#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2021/7/21 20:11
@Author  : Xu_Jian
"""
import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind('tcp://*:5555')

while True:
    message = socket.recv()
    print(type(message))
    print('received request: ', message)
    time.sleep(1)
    if message == 'hello':
        socket.send('World')
    else:
        socket.send('success')