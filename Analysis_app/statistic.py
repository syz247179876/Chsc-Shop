# -*- coding: utf-8 -*-
# @Time  : 2020/8/21 下午10:56
# @Author : 司云中
# @File : statistic.py
# @Software: Pycharm
import datetime

from django.contrib.auth.models import User

from Analysis_app.signals import login_user_browser_times, user_browser_times
from e_mall.base_redis import BaseRedis
from e_mall.loggings import Logging

common_logger = Logging.logger('django')


class StatisticRedis(BaseRedis):
    """redis统计类"""

    def __init__(self, redis_instance):
        self.connect()
        super().__init__(redis_instance)

    def connect(self):
        """注册信号"""
        login_user_browser_times.connect(self.statistic_login_user_browsing_times, sender=User)
        user_browser_times.connect(self.statistic_user_browsing_times, sender=None)

    @staticmethod
    def trans_date(date):
        """
        date ->  str
        :return:
        """
        date_str = datetime.date.strftime(date, "%Y-%m-%d")
        return date_str

    @staticmethod
    def trans_date_offset(date):
        """
        date -> str (offset)
        :return: year , month, day
        """
        date_str = datetime.date.strftime(date, "%Y-%m-%d")
        date_list = date_str.split('-')
        return date_list[0], date_list[1], int(date_list[2])

    def statistic_login_user_browsing_times(self, sender, instance, date, **kwargs):
        """
        1.统计当天用户登录的总人数
        每天24：00点，执行定时任务，统计后以key-value存储，释放bitmap空间

        2.统计某用户每月登录的次数，按月大统计一次
        每月第一天，执行定时任务，统计后，释放bitmap空间
        :param sender:  发送者
        :param instance: User实例
        :param date:   当天日期
        :param kwargs:  额外参数
        :return:
        """
        pipe = self.redis.pipeline()
        date_str = self.trans_date(date)                 # offset:user_pk
        key = self.key('login-day', date_str)
        pipe.setbit(key, instance.pk, 1)

        year, month, day = self.trans_date_offset(date)  # offset:day
        key = self.key('login', year, month, instance.pk)
        pipe.setbit(key, day, 1)  # 尽可能节约内存
        pipe.execute()

    def statistic_user_browsing_times(self, sender, ip, date, **kwargs):
        """
        统计每天登录网站浏览的次数
        :param sender: 发送者
        :param date:  日期类型
        :param kwargs: 额外参数
        :return:
        """
        date_str = self.trans_date(date)
        hash_key = self.key('browser-day', date_str)
        pipe = self.redis.pipeline()
        if pipe.hexists(hash_key, ip):
            pipe.hincrby(hash_key, ip)
        else:
            pipe.hset(hash_key, ip, 1)
        pipe.execute()


statistic_redis = StatisticRedis.choice_redis_db('analysis')
