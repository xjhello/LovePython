# -*- coding: utf-8 -*-
from queue import Queue
import signal
import sys
import threading
import time
import traceback


def output_tracebacks(signum, frame):
    id2thread = {}
    for thread in threading.enumerate():
        id2thread[thread.ident] = thread
    for thread_id, stack in sys._current_frames().items():
        stack_list = traceback.format_list(traceback.extract_stack(stack))
        print('thread {}:'.format(id2thread[thread_id]))
        print(''.join(stack_list))


def setup_backdoor():
    signal.signal(signal.SIGUSR1, output_tracebacks)


def worker(q):
    while True:
        task = q.get()
        if task is None:
            break
        # do something with task
        time.sleep(1.2)


def producer(q):
    for x in range(100):
        q.put(x)
        time.sleep(1)
    q.put(None)


setup_backdoor()
q = Queue()
t1 = threading.Thread(target=producer, args=(q,))
t1.start()
t2 = threading.Thread(target=worker, args=(q,))
t2.start()
for t in [t1, t2]:
    t.join()