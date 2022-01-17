#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2021/10/3 10:57
@Author  : Xu_Jian
"""
import asyncio
import requests

async def coroutine_example(name):
    print('正在执行name:', name)
    await asyncio.sleep(1)
    print('执行完毕name:', name)

loop = asyncio.get_event_loop()

# tasks = [coroutine_example('Zarten_' + str(i)) for i in range(3)]
tasks = [coroutine_example('Zarten_'),  coroutine_example('Zarten_111111')]
print("task:  ", tasks)
wait_coro = asyncio.wait(tasks)
loop.run_until_complete(wait_coro)
loop.close()