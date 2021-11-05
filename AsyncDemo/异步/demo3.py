#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2021/10/3 10:09
@Author  : Xu_Jian
"""
def coroutine_example(name):
    print('start coroutine_example ,在yield暂停', name)
    x = yield name #调用next()时，产出yield右边的值后暂停；调用send()时，产出值赋给x，并往下运行
    print('send值:', x)
    return 'zhihuID: Zarten'

def grouper2():
    print("grouper2 >>>>")
    print("产出 yield from 右边的值后暂停 ")
    result2 = yield from coroutine_example('Zarten') #在此处暂停，等待子生成器的返回后继续往下执行
    print('result2的值：', result2)
    return result2

def grouper():
    print("grouper >>>>")
    print("产出 yield from 右边的值后暂停 ")
    result = yield from grouper2() #在此处暂停，等待子生成器的返回后继续往下执行
    # result = yield  grouper2() # 没有from的话就不会进入到子函数里面
    print('result的值：', result)
    return result

def main():
    g = grouper()
    next(g)
    # try:
    #     g.send(10)
    # except StopIteration as e:
    #     print('返回值：', e.value)

if __name__ == '__main__':
    main()