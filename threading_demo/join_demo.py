#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import time


def a():
    c = 0
    while True:
        if c == 5:
            break
        c+=1
        time.sleep(1)
        print("a:{}".format(c))

def b():
    c = 0
    while True:
        if c == 7:
            break
        c+=1
        time.sleep(1)
        print("b:{}".format(c))

ta = threading.Thread(target=a)
tb = threading.Thread(target=b)
ta.start()
tb.start()

ta.join()
tb.join()
"""
join所完成的工作就是线程同步
即主线程任务结束之后，进入阻塞状态，一直等待其他的子线程执行结束之后，主线程在终止
"""
print("子线程大爷们，都结束了我才结束")