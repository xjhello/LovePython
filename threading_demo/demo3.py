#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import time


def t1():
    print("t1 start")
    time.sleep(2)
    print("t1 end")

def t2():
    print("t2 start")
    time.sleep(2)
    print("t2 end")

tt1 = threading.Thread(target=t1)
tt2 = threading.Thread(target=t2)
print(tt1.name)