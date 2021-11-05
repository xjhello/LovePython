#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2021/9/30 20:25
@Author  : Xu_Jian
"""
import time


def coroutine_example(name):
    """有yield关键字即为生成器函数"""
    print('函数执行', name)
    # 调用next()时，产出yield右边的值后暂停；调用send()时，产出值赋给x，并往下运行
    # 调用next()时相当于list.append(x)
    print("next() 遇到yield弹出name：", name, "暂停等待x 赋值")
    x = yield name + ">>>>>>" # next()在此暂停
    # 如调用next() x=None
    # 调用send()时，产出值赋给x，并往下运行
    print('send后,接受的值赋值给x = ', x, '后, 前往下一yield')
    # send的值赋值给y
    sss = "sada"
    print("遇到yield暂停并且弹出右边的值 ：",sss )
    y = yield sss # send()在此暂停

    print("再一个next触发, 赋值")
    print('222send值:',y)

print(">>>>>初始化函数")
coro = coroutine_example('Zarten')
print(">>>>>调用next")
print('next的返回值:', next(coro))
print("----" * 20)
print('next的返回值:', next(coro))
# print('next的返回值:', next(coro))
# print('next的返回值:', next(coro))
# send时接收值的是yield左边的值a
# print(">>>>>调用send")
# print('send的返回值:', coro.send("send data"))
# print('next的返回值:', next(coro))
# print('next的返回值:', coro.__next__())
# print('next的返回值:', next(coro))
# print('next的返回值:', next(coro))
# print('send的返回值:', coro.send(6))
