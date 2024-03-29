#!/usr/bin/env python
# -*- coding: utf-8 -*-
from celery import Celery
app = Celery('tasks', broker='amqp://guest@localhost//')

@app.task
def add(x, y):
    return x + y