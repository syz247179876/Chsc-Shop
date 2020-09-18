# -*- coding: utf-8 -*-
# @Time  : 2020/8/18 上午11:40
# @Author : 司云中
# @File : celery_learn.py
# @Software: Pycharm
import single_mode

# from celery import Celery
#
# BROKER_URL = 'redis://:123456@127.0.0.1:6379/0'
# CELERY_RESULT_BACKEND = 'redis://:123456@127.0.0.1:6379/1'
# app = Celery('tasks', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)
# app.conf.beat_schedule = {
#     # Executes every Monday morning at 7:30 a.m.
#     'add-every-monday-morning': {
#         'task': 'tasks.add',
#         'schedule': 5.0,
#         'args': (16, 16),
#     },
# }
#
# @app.task
# def add(x, y): return x + y
#
#
# task_line = add.s(1, 2) | add.s(3, 4)  # 形成一个任务链
#
# # print(add.default_retry_delay)  # app.work
# # print(app.conf.timezone)  # app的市区配置
# # print(add.__class__.mro())
# # print(add.delay(2, 3))
# m = add.apply_async(args=(2,4))
# print(type(m))
