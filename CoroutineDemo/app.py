# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
协程（Coroutine），也可以被称为微线程，
是一种用户态内的上下文切换技术。简而言之，其实就是通过一个线程实现代码块相互切换执行
上述代码是普通的函数定义和执行，按流程分别执行两个函数中的代码，
并先后会输出：1、2、3、4。但如果介入协程技术那么就可以实现函数见代码切换执行，最终输入：1、3、2、4
"""
def func1():
    print(1)
    ...
    print(2)
def func2():
    print(3)
    ...
    print(4)
func1()
func2()
"""
greenlet，是一个第三方模块，用于实现协程代码（Gevent协程就是基于greenlet实现）
yield，生成器，借助生成器的特点也可以实现协程代码。
asyncio，在Python3.4中引入的模块用于编写协程代码。
async & awiat，在Python3.5中引入的两个关键字，结合asyncio模块可以更方便的编写协程代码
"""
### yield
### yield解釋：带yield的函数是一个生成器
#https://www.cnblogs.com/linhaifeng/p/7278389.html
def foo():
    print("starting...")
    while True:
        res = yield 4
        print("res:",res)
g = foo()
print(next(g))
print("*"*20)
print(next(g))

def func1():
    print("###")
    yield 1  # 暂存函数的状态
    yield from func2()
    yield 2

def func2():
    yield 3
    yield 4
f1 = func1()
for item in f1:
    print("***", item)
    print(item)

### asyncio

import asyncio
print("+++++++++++++")
@asyncio.coroutine
def func1():
    print(1)
    yield from asyncio.sleep(2)  # 遇到IO耗时操作，自动化切换到tasks中的其他任务
    print(2)
@asyncio.coroutine
def func2():
    print(3)
    yield from asyncio.sleep(2) # 遇到IO耗时操作，自动化切换到tasks中的其他任务
    print(4)
tasks = [
    asyncio.ensure_future( func1() ),
    asyncio.ensure_future( func2() )
]
# 生成事件循环列表 while True 去遍历任任务  查看哪个任务可执行 可执行立马执行 不可执行(IO堵塞)忽略
loop = asyncio.get_event_loop()
#
loop.run_until_complete(asyncio.wait(tasks))