# -*- coding: utf-8 -*-
# @Time  : 2020/11/15 下午1:47
# @Author : 司云中
# @File : tasks.py
# @Software: Pycharm
import datetime

from Emall import celery_apps as app
from Emall import manage_redis
from search_app.redis.history_redis import history_redis
from search_app.signals import record_search


@app.task
def timer_eliminate_heat():
    """定时清除每日的热搜榜"""
    with manage_redis('search', type(history_redis)) as redis:
        date = datetime.datetime.today() - datetime.timedelta(1)
        redis.delete(history_redis.heat_key(date))


@app.task
def record_user_search(user_id, keyword):
    """记录用户搜索记录"""
    record_search.send(sender=user_id, keyworkd=keyword)


