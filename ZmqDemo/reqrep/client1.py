#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2021/7/21 20:12
@Author  : Xu_Jian
"""
import zmq

context = zmq.Context()
print('connect to hello world server')

socket = context.socket(zmq.REQ)
socket.connect('tcp://localhost:5555')

for request in range(1, 10):
    print('send ', request, '...')

    socket.send('hello')
    # socket.send_string('hello')
    message = socket.recv()
    print('received reply ', request, '[', message, ']')
