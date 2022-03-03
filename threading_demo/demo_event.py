#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import time

"""
基于Event事件通讯
"""
class Son():
    def __init__(self, main_a):
        print("初始化：{}".format(main_a))
        self.main_a = main_a
        # threading.Thread(target=self.change).start()
        # threading.Thread(target=self.change1, args=(main_a,)).start()
        threading.Thread(target=self.change1, args=(self.main_a,)).start()

    def change(self):
        while True:
            if isinstance(self.main_a, int):
                self.main_a += 1
                print("修改后", self.main_a)
            if isinstance(self.main_a, list):
                self.main_a.append(1)
                print("修改后", self.main_a)

            if isinstance(self.main_a, threading.Event):
                if self.main_a.isSet():
                    self.main_a.clear()
                else:
                    self.main_a.set()
                print("修改后", self.main_a)
            time.sleep(1)

    def change1(self, data):
        while True:
            if isinstance(data, int):
                data+= 1
                print("修改后", data)
            if isinstance(data, list):
                data.append(1)
                print("修改后", data)

            if isinstance(data, threading.Event):
                if data.isSet():
                    data.clear()
                else:
                    data.set()
                print("修改后", data)
            time.sleep(1)

class Main():
    def __init__(self):
        # 传入不可变类型 子类线程无法改变
        # self.Main_a = 0
        # 传入的是可变类型 子类改变父类能感知
        self.Main_a = [0]
        # self.Main_a = threading.Event()

        self.son = Son(self.Main_a)
        threading.Thread(target=self.read).start()

    def read(self):
        while True:
            if isinstance(self.Main_a, threading.Event):
                print("读取1: ", self.Main_a.isSet())
            else:
                print("读取1: ", self.Main_a)
            time.sleep(1)
Main()
