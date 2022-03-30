#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import time


def a():
    c = 0
    while True:
        if c == 10:
            break
        c+=1
        time.sleep(1)
        print("a:{}".format(c))

def b():
    c = 0
    while True:
        if c == 20:
            break
        c+=1
        time.sleep(1)
        print("b:{}".format(c))

# ta = threading.Thread(target=a)
# tb = threading.Thread(target=b)
# ta.start()
# tb.start()
# # ta.join()
# # tb.join()
# print(1111)
aa = [1,2,1,21,2,1]

bb = [i for i in aa]
print(bb)
print(all(bb))