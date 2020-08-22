# -*- coding: utf-8 -*-
# @Time  : 2020/8/22 下午8:03
# @Author : 司云中
# @File : tasks.py
# @Software: Pycharm

from e_mall.celery import app
from e_mall.loggings import Logging
from django_redis import get_redis_connection
common_logger = Logging.logger('django')


@app.task
def statistic_login_times(x,y ):
    """发送统计每日用户活跃量的定时信号"""

    redis = get_redis_connection('analysis')
    redis.incrby('syz')
    common_logger.info('success')