#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/22 11:46 上午
# @Author  : Xujian
import redis   # 导入redis 模块

r = redis.Redis(host='localhost', port=6379, db=11)
# r.set('name', 'runoob')  # 设置 name 对应的值
# print(r['name'])
# print(r.get('name'))  # 取出键 name 对应的值
# print(type(r.get('name')))  # 查看类型

r.hset("hash1", "k1", "v1")
r.hset("hash1", "k2", "v2")
r.hmset("hash2", {"k2": "v2", "k3": "v3"})
print(r.hkeys("hash1")) # 取hash中所有的key
print(r.hget("hash1", "k1"))    # 单个取hash的key对应的值
print(r.hmget("hash1", "k1", "k2")) # 多个取hash的key对应的值
r.hsetnx("hash1", "k2", "v3") # 只能新建
print(r.hget("hash1", "k2"))


r.lpush("list1", 11, 22, 33)
print(r.lrange('list1', 0, -1))

r.sadd("set1", 33, 44, 55, 66)  # 往集合中添加元素
print(r.scard("set1"))  # 集合的长度是4
print(r.smembers("set1"))   # 获取集合中所有的成员


# r.zadd("zset1", n1=11, n2=22)
r.zadd("zset2", 'm1', 22, 'm2', 44)
print(r.zcard("zset1")) # 集合长度
print(r.zcard("zset2")) # 集合长度
print(r.zrange("zset1", 0, -1))   # 获取有序集合中所有元素
print(r.zrange("zset2", 0, -1, withscores=True))   # 获取有序集合中所有元素和分数