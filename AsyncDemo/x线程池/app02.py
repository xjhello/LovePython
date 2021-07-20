#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2021/7/20 14:36
@Author  : Xu_Jian
"""
import time
from concurrent.futures import ThreadPoolExecutor as Pool
import requests

URLS = ['http://www.baidu.com', 'http://qq.com', 'http://sina.com']

"""
这个方法返回一个map(func, *iterables)迭代器，迭代器中的回调执行返回的结果有序的
"""

def task(url, timeout=10):
    print(time.time())
    return requests.get(url, timeout=timeout)


pool = Pool(max_workers=3)
results = pool.map(task, URLS)

for ret in results:
    print('%s, %s' % (ret.url, len(ret.content)))

