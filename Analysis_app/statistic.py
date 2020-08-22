# -*- coding: utf-8 -*-
# @Time  : 2020/8/21 下午10:56
# @Author : 司云中
# @File : statistic.py
# @Software: Pycharm
import datetime

from django.contrib.auth.models import User

from Analysis_app.signals import login_user_browser_times, user_login_mouth, user_browser_times
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
        user_login_mouth.connect(self.statistic_user_mouth,sender=User)
        user_browser_times.connect(self.statistic_user_browsing_times, sender=None)
        common_logger.info('注册成功！')

    def trans_date(self, date):
        """
        date ->  str
        :return:
        """
        date_str = datetime.date.strftime(date, "%Y-%m-%d")
        return date_str


    def statistic_login_user_browsing_times(self, sender, instance, date, **kwargs):
        """
        统计当天用户登录的总次数
        每天24：00点，发布定时任务，统计后以key-value存储，释放bitmap空间
        :param sender:  发送者
        :param instance: User实例
        :param date:   当天日期
        :param kwargs:  额外参数
        :return:
        """
        date_str = self.trans_date(date)
        key = self.key('login-day',date_str)
        self.redis.setbit(key, instance.pk)

    def statistic_user_mouth(self, sender, instance, date, **kwargs):
        """
        统计每月登录的用户个数
        :param sender:  发送者
        :param instance: User实例
        :param date:   当天日期
        :param kwargs:  额外参数
        :return:
        """
        date_str = self.trans_date(date)
        key = self.key('login-mouth', instance.pk)
        # self.redis.setbit(key,)

    def statistic_user_browsing_times(self, sender, ip, date, **kwargs):
        """
        统计每天登录网站浏览的次数
        :param sender:
        :param date:
        :param kwargs:
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
        return 'success'


statistic_redis = StatisticRedis.choice_redis_db('analysis')

