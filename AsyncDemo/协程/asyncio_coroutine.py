#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/18 4:15 下午
# @Author  : Xujian
import asyncio
import aiohttp

@asyncio.coroutine
def fetch_page(session, url):
   response = yield from session.get(url)
   if response.status == 200:
       text = yield from response.text()
       print(text)
loop = asyncio.get_event_loop()

session = aiohttp.ClientSession(loop=loop)

tasks = [
   asyncio.ensure_future(
      fetch_page(session, "http://www.baidu.com")),
   asyncio.ensure_future(
      fetch_page(session, "http://www.baidu.com"))
]

loop.run_until_complete(asyncio.wait(tasks))
session.close()
loop.close()