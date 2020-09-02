# -*- coding: utf-8 -*-
# @Time  : 2020/8/22 下午8:03
# @Author : 司云中
# @File : tasks.py
# @Software: Pycharm
import datetime

from e_mall.base_redis import BaseRedis
from e_mall import celery_apps as app
from e_mall.loggings import Logging
from django_redis import get_redis_connection
common_logger = Logging.logger('django')


@app.task
def statistic_login_times():
    """发送统计每日用户活跃量的定时信号"""
    date_str = datetime.date.strftime(datetime.date.today() - datetime.timedelta(1),'%Y-%m-%d')
    base_redis = BaseRedis.choice_redis_db('analysis')
    key = base_redis.key('login-day', date_str)
    pipe = base_redis.redis.pipeline()
    times = pipe.bitcount(key, 0,-1)    # 统计当天登录的用户次数
    pipe.delete(key)               # 删除bitmap
    pipe.set(key, times)      # 设置新key-value统计每日的用户
    pipe.execute()