#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2021/10/2 1:23
@Author  : Xu_Jian
"""
def a():
    print("开始")
    a = yield 1
    print("结束", a)

aa = a()
print(next(aa)  )
print(next(aa)  )
# next(aa)


