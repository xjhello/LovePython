#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2021/7/15 17:42
@Author  : Xu_Jian
"""
import concurrent.futures
import requests
import threading
import time

def download_one(url):
    try:
        print("request :{}".format(url))
        # resp = requests.get(url)
        # print('Read {} from {}'.format(len(resp.content), url))
    except Exception as ex:
        print(ex)

def download_all(url):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(download_one, url)
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     results = executor.map(download_one,sites)


def download_all1(sites):
    # future列表中每个future完成的顺序，和它在列表中的顺序并不一定完全一致。
    # 到底哪个先完成、哪个后完成，取决于系统的调度和每个future的执行时间
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        to_do = []
        for site in sites:
            # executor.submit返回future实例
            future = executor.submit(download_one, site)
            print("future ：{}".format(future))
            to_do.append(future)
            # future.add_done_callback(over)

        # 在futures完成后打印结果
        for future in concurrent.futures.as_completed(to_do):
            if future.exception() is not None:
                print(future.exception())
            else:
                print(future.result())

def main():
    sites = [
        'https://en.wikipedia.org/wiki/Portal:Arts',
        'https://en.wikipedia.org/wiki/Portal:History',
        'https://en.wikipedia.org/wiki/Portal:Society',
        'https://en.wikipedia.org/wiki/Portal:Biography',
        'https://en.wikipedia.org/wiki/Portal:Mathematics',
    ]
    start_time = time.perf_counter()
    download_all1(sites)
    end_time = time.perf_counter()
    print('Download {} sites in {} seconds'.format(len(sites), end_time - start_time))

if __name__ == '__main__':
    main()

#