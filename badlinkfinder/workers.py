#!/usr/bin/env python3
# coding: utf-8

from queue import Queue
from threading import Thread

import traceback

class WorkerManager(object):    
    # Pool of workers(threads) consuming tasks from a queue
    def __init__(self, worker_count=5):
        # Queue with tasks that need to be processed.
        self._tasks = Queue()
        self._buffer = []

        # Might want to make this dynamic based on # of events in queue.
        for _ in range(worker_count):
            Worker(self)


    def _add_queue(self, url):
        if self.buffer:
            while not self.queue.full() and self.buffer:
                self.queue.put(self.buffer.pop())
            self.buffer.append(url)
        else:
            if self.queue.full():
                self.buffer.append(url)
            else:
                self.queue.put(url)

    # func is the function that is run with the provided args and kwargs. Store tasks in buffer in case task queue is full
    def add_task(self, func, *args, **kwargs):
        if self._buffer:
            while not self._tasks.full() and self._buffer:
                self._tasks.put(self._buffer.pop())
            self._buffer.append((func, args, kwargs))
        else:
            if self._tasks.full():
                self._buffer.append((func, args, kwargs))
            else:
                self._tasks.put((func, args, kwargs))

    def wait_complete(self):
        # Wait for all tasks to complete
        self._tasks.join()

class Worker(Thread):
    def __init__(self, manager, *args):
        Thread.__init__(self)
        self._manager = manager
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kwargs = self._manager._tasks.get()
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(e)
                traceback.print_tb(e.__traceback__)
            finally:
                self._manager._tasks.task_done()
