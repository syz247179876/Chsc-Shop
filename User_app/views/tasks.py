# -*- coding: utf-8 -*-
# @Time : 2020/5/1 09:42
# @Author : 司云中
# @File : tasks.py
# @Software: PyCharm

import datetime

from e_mall import celery_app as app


@app.task
def delete_outdated(self):
    """timed task:delete obsolete key-value"""
    now = datetime.datetime.now()
    delta = datetime.timedelta(-1)
    previous = now - delta
    key = previous.strftime('%Y-%m-%d')
    self.redis.delete(key)
