#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import time
"""
main线程又可以启动其他线程。当所有线程都运行结束时，进程结束。
如果有一个线程没有退出，进程就不会退出。所以，必须保证所有线程都能及时结束
如果这个线程不结束，进程就无法结束。问题是，由谁负责结束这个线程？
有一种线程，它是在后台运行的，它的任务是为其他线程提供服务，这种线程被称为“后台线程（Daemon Thread）”，
又称为“守护线程”或“精灵线程”。Python 解释器的垃圾回收线程就是典型的后台线程。
后台线程有一个特征，如果所有的前台线程都死亡了，那么后台线程会自动死亡。
"""

"""
非常明显的看到，主线程结束以后，子线程还没有来得及执行，整个程序就退出了。
"""

def run():
    while True:
        time.sleep(2)
        print('当前守护线程的名字是： \n', threading.current_thread().name)
        time.sleep(2)


if __name__ == '__main__':

    start_time = time.time()

    print('这是主线程：', threading.current_thread().name)
    thread_list = []
    for i in range(5):
        t = threading.Thread(target=run)
        thread_list.append(t)

    for t in thread_list:
        # 守护线程就是后台线程 非守护线程结束  他就要立马死掉。
        t.setDaemon(True)
        t.start()
    time.sleep(3)
    print("非守护线程全部死掉，守护线程也立马陪我一起死")
    # 所有非守护线程结束后 守护线程立马死掉！
    print('主线程结束了！' , threading.current_thread().name)
    print('一共用时：', time.time()-start_time)
