# -*- coding: utf-8 -*-
# @Time  : 2020/8/22 下午8:03
# @Author : 司云中
# @File : tasks.py
# @Software: Pycharm
import datetime

from Analysis_app.statistic import statistic_redis
from e_mall import celery_apps as app
from e_mall.loggings import Logging

common_logger = Logging.logger('django')


@app.task
def statistic_login_times():
    """发送统计每日用户活跃量的定时信号"""
    date_str = datetime.date.strftime(datetime.date.today() - datetime.timedelta(1),'%Y-%m-%d')
    key = statistic_redis.key('login-day', date_str)
    pipe = statistic_redis.redis.pipeline()
    times = pipe.bitcount(key, 0,-1)    # 统计当天登录的用户次数
    pipe.delete(key)               # 删除bitmap
    pipe.set(key, times)      # 设置新key-value统计每日的用户
    pipe.execute()


@app.task
def statistic_buy_category_day():
    """
    每日统计购买商品的种类,获取前一天购买次数最多的商品种类
    清除前一天之前的所有记录（正常不需要清除，以防止不同步出问题）
    重新开个sorted set 插入前一天的获胜的商品种类，以月为key
    """
    today = datetime.date.today()
    yesterday = today + datetime.timedelta(-1)                               # 昨天date
    month_str = statistic_redis.trans_month(today)                           # 今天所在的月
    yesterday_str = statistic_redis.trans_date(yesterday)
    month_zset_key = statistic_redis.key('buy-category', month_str)          # key of current month
    yesterday_zset_key = statistic_redis.key('buy-category', yesterday_str)  # key of yesterday
    pipe = statistic_redis.redis.pipeline()
    # 选择pop or range都可以
    # 格式：[(b'first', 20.0), (b'second', 19.0), (b'third', 18.0)]
    winner = pipe.zpopmax(yesterday_zset_key)                                # 弹出排名第一的商品种类
    # pipe.zrevrange(yesterday_zset_key, 0, 8, withscors=True)              # (value,score) double tuple

    pipe.zadd(month_zset_key, {result_tuple[0].decode(): result_tuple[1] for result_tuple in winner})                                              # 添加到新的以月为key的有序集合中
    pipe.delete(yesterday_zset_key)
    pipe.execute()


@app.task
def clear_user_browsing_times():
    """定时清除当天用户浏览次数"""
    today = datetime.date.today()
    yesterday = today + datetime.timedelta(-1)  # 昨天date
    yesterday_str = statistic_redis.trans_date(yesterday)
    key = statistic_redis.key('browser-day', yesterday_str)
    statistic_redis.redis.delete(key)



