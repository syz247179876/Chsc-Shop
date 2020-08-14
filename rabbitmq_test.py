# -*- coding: utf-8 -*-
# @Time  : 2020/8/5 上午11:38
# @Author : 司云中
# @File : rabbitmq_test.py
# @Software: Pycharm

from celery import Celery
from celery.result import AsyncResult

app = Celery('rabbitmq_test', broker='amqp://syz:syzxss247179876@0.0.0.0:5672//')


@app.task
def test(x,y):
    return x + y


res = test.delay(1,5)
print(res.id)