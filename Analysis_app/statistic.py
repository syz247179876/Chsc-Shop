# -*- coding: utf-8 -*-
# @Time  : 2020/8/21 下午10:56
# @Author : 司云中
# @File : statistic.py
# @Software: Pycharm
import datetime

from django.contrib.auth.models import User

from Analysis_app.signals import login_user_browser_times, user_browser_times, buy_category, user_recommend
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
        login_user_browser_times.connect(self.record_login_user_browsing_times, sender=User)
        user_browser_times.connect(self.record_user_browsing_times, sender=None)
        buy_category.connect(self.record_buy_category, sender=None)
        user_recommend.connect(self.record_user_recommendation, sender=None)
        common_logger.info('success')

    @staticmethod
    def trans_date(date):
        """
        date ->  str
        :return: str
        """
        date_str = datetime.date.strftime(date, "%Y-%m-%d")
        return date_str

    @staticmethod
    def trans_month(date):
        """
        date -> str
        :return: str
        """
        month_str = datetime.date.strftime(date, "%Y-%m")
        return month_str

    @staticmethod
    def trans_date_offset(date):
        """
        date -> str (offset)
        :return: year , month, day
        """
        date_str = datetime.date.strftime(date, "%Y-%m-%d")
        date_list = date_str.split('-')
        return date_list[0], date_list[1], int(date_list[2])

    def record_login_user_browsing_times(self, sender, instance, **kwargs):
        """
        1.记录当天用户登录的总人数
        每天24：00点，执行定时任务，统计后以key-value存储，释放bitmap空间

        2.记录某用户每月登录的次数，按月大统计一次
        每月第一天，执行定时任务，统计后，释放bitmap空间
        :param sender:  发送者
        :param instance: User实例
        :param kwargs:  额外参数
        :return:
        """
        date = datetime.date.today()  # today
        pipe = self.redis.pipeline()
        date_str = self.trans_date(date)                 # offset:user_pk
        key = self.key('login-day', date_str)
        pipe.setbit(key, instance.pk, 1)

        year, month, day = self.trans_date_offset(date)  # offset:day
        key = self.key('login', year, month, instance.pk)
        pipe.setbit(key, day, 1)  # 尽可能节约内存
        pipe.execute()

    def record_user_browsing_times(self, sender, ip, **kwargs):
        """
        记录每天网站访问量
        :param sender: 发送者
        :param date:  日期类型
        :param kwargs: 额外参数
        :return:
        """

        date = datetime.date.today()  # today
        date_str = self.trans_date(date)
        key = self.key('browser-day', date_str)
        self.redis.incrby(key, amount=1)

    def record_user_recommendation(self, sender, category, instance, **kwargs):
        """
        每个用户维护一个hash表，hash表内部填充用户收入收藏夹的商品种类，浏览足迹商品的种类，购买商品的种类的次数
        生存周期3天，以便实时喂给算法新的数据集,同时避免占用过多内存
        :param sender: 发送者
        :param category: 种类
        :param instance: User实例
        :param kwargs: 额外参数
        :return:
        """

        pipe = self.redis.pipeline()
        hash_key = self.key('love-category', instance.pk)
        pipe.zincrby(hash_key, amount=1, value=category) # 默认从1开始
        pipe.expire(hash_key, 259200)    # 活三天
        pipe.execute()


    def record_buy_category(self, sender, category, date, **kwargs):
        """
        当用户购买某一商品后，记录该商品种类被购买+1
        用于每一天哪些类型的商品销售量多---> 每一月 ----> 每一季度 ----> 每一年
        有序集合，以日为key
        :param sender:发送者
        :param category:商品类型
        :param kwargs:额外参数
        :return:
        """
        date = datetime.date.today()  # today
        date_str = self.trans_date(date)
        zset_key = self.key('buy-category', date_str)
        self.redis.zincrby(zset_key, amount=1, value=category)  # 默认为1,方便排行




statistic_redis = StatisticRedis.choice_redis_db('analysis')
