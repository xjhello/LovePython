#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/18 4:17 下午
# @Author  : Xujian
import asyncio
import aiohttp


"""
在 Python 中，协程也是 awaitable 对象，collections.abc.Coroutine 对象继承自 collections.abc.Awaitable
asyncio 实质担当的角色是一个异步框架，async/await 是为异步框架提供的 API
"""


async def fetch_page(session, url):
   response = await session.get(url)
   if response.status == 200:
       text = await response.text()
       print(text)

loop = asyncio.get_event_loop()
session = aiohttp.ClientSession(loop=loop)

tasks = [
   asyncio.ensure_future(
       fetch_page(session, "http://bigsec.com/products/redq/")),
   asyncio.ensure_future(
       fetch_page(session, "http://bigsec.com/products/warden/"))
]
loop.run_until_complete(asyncio.wait(tasks))
session.close()
loop.close()