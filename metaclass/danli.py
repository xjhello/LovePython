#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/24 5:13 下午
# @Author  : Xujian
class Single(object):
    _instance = None
    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance
    def __init__(self):
        pass
