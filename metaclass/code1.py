#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/24 3:06 下午
# @Author  : Xujian
# 在元类中控制把自定义类的数据属性都变成大写


class AA(type):
    def __new__(cls, *args, **kwargs):
        print(*args)
        print(**kwargs)
        return type.__new__(cls, *args, **kwargs)

AA()


# class aa(AA):
#     def __init__(self):
#         print(111)
# aa()
class Mymetaclass(type):
    def __new__(cls,name,bases,attrs):
        updata_attrs = {}
        for k,v in attrs:
            # 函数用于检查一个对象是否是可调用的
            if not callable(v) and not k.startswith('__'):
                updata_attrs[k.upper()] = v
            else:
                updata_attrs[k] = v
        return type.__new__(cls, name,bases,attrs)