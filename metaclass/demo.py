#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/24 2:22 下午
# @Author  : Xujian

"""
所有的对象都是实例化或者说调用类而得到的（调用类的过程称为类的实例化）
类的产生过程其实就是元类的调用过程
"""

class A(object):
    def __new__(cls, *args, **kwargs):
        # 返回的是实例
        print("A __new__")
        return super(A, cls).__new__(cls, *args, **kwargs)

    def __init__(self):
        print("A __init__")

# A()

# 输出绝对值
class Int(int):
    def __new__(cls, v):
        print(1111)
        return super(Int, cls).__new__(cls, abs(v))
    
    # def __init__(self):
    #     print(2222)
    #     super(Int, self).__init__()



a = Int(1)
# print(type(a))
# # 元类type实例化A。
# print(type(A))
#  我们用class关键字定义的类本身也是一个对象，负责产生该对象的类称之为元类（元类可以简称为类的类），内置的元类为type
