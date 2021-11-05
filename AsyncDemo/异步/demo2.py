#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2021/10/2 22:18
@Author  : Xu_Jian
"""


def for_test():
    print("开始")
    for i in range(3):
        print('>>> ', i)
        yield i

print("有yield 有迭代操作才触发")
for_test()
print("list 迭代触发")
print("list >> ", list(for_test()))


def yield_from_test():
    # 其实yield from内部会自动捕获StopIteration异常，
    # 并把异常对象的value属性变成yield from表达式的值。
    yield from range(3)

# print(111)
# yield_from_test()
# print(222)
# print(list(yield_from_test()))
for i in yield_from_test():
    print(i)