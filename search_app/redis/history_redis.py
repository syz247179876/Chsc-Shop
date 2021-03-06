# -*- coding: utf-8 -*-
# @Time  : 2020/11/14 下午7:37
# @Author : 司云中
# @File : history_redis.py
# @Software: Pycharm
import datetime
from time import time

from Emall.base_redis import BaseRedis, manage_redis
from Emall.exceptions import TypeTransformError
from search_app import signals
from user_app.redis.favorites_redis import RedisFavoritesOperation


def client_key(func):
    """获取client的key装饰器"""

    def decorate(self, sender, request, keyword, **kwargs):
        if sender is None:  # 如果用户未登录
            sender = BaseRedis.get_client_ip(request=request)  # 获取客户端IP
        return func(self, sender, keyword, **kwargs)
    return decorate


class HistoryRedisOperation(BaseRedis):
    DB = 'search'

    def __init__(self, db, redis):
        super().__init__(db, redis)
        self.connect()

    def connect(self):
        signals.record_search.connect(self.save_search, sender=None)
        signals.del_search_single.connect(self.delete_single_search, sender=None)
        signals.del_search_all.connect(self.delete_all_search, sender=None)
        signals.retrieve_record.connect(self.retrieve_record, sender=None)
        signals.retrieve_heat_keyword.connect(self.get_cur_heat_keyword, sender=None)  # 获取当天热搜
        signals.retrieve_heat_keyword.connect(self.get_prev_heat_keyword, sender=None)  # 获取前天热度

    @property
    def score(self):
        return int(time())

    @staticmethod
    def user_key(key):
        return f'user-history-{key}'

    @staticmethod
    def heat_key(date):
        return f'heat-{date.strftime("%Y-%m-%d")}'

    @client_key
    def save_search(self, sender, key, **kwargs):
        """
        记录某用户的浏览记录
        有效时间1个月
        """
        with manage_redis(self.DB, type(self)) as redis:
            # 为每个用户维护一个搜索有序集合
            # 为所有关键词维护一个有序集合,用于分析
            with redis.pipeline() as pipe:
                pipe.zadd(self.user_key(sender), {key: self.score})  # 时间复杂度O(log(N))
                pipe.zincrby(self.heat_key(datetime.datetime.today()), 1, key)  # 将该关键字添加到热搜有序集合中,如果存在key,则+1,不存在设置为1
                pipe.execute()

    @client_key
    def delete_single_search(self, sender, key, **kwargs):
        """
        单删某条搜索历史记录
        """
        with manage_redis(self.DB, type(self)) as redis:
            return redis.zrem(self.user_key(sender), key)

    @client_key
    def delete_all_search(self, sender, **kwargs):
        """
        群删所有搜索历史记录
        """
        with manage_redis(self.DB, type(self)) as redis:
            return redis.delete(self.user_key(sender))

    @client_key
    def retrieve_record(self, sender, **kwargs):
        """
        根据分页获取最新的搜索记录
        默认为10条
        """

        # with 生存周期持续到函数结束
        with manage_redis(self.DB, type(self)) as redis:
            request = kwargs.pop('request')
            try:  # 检查类型,类型错误,抛出异常,由RedisOperationError捕获
                page = int(request.query_params.get('page', '1'))
                limit = int(request.query_params.get('limit', '10'))
            except ValueError:
                raise TypeTransformError()
            result = redis.zrevrange(self.user_key(sender), (page - 1) * limit, page * limit)  # 返回分数从高到低的前十个(时间最近的前十个)
            return result

    def get_cur_heat_keyword(self, sender, **kwargs):
        """
        每日热搜
        动态获取每日的前十位热度搜索关键词
        """
        with manage_redis(self.DB, type(self)) as redis:
            date = datetime.datetime.today()
            return redis.zrevrange(self.heat_key(date), 0, 10)  # 前十大热搜


    def get_prev_heat_keyword(self, sender, **kwargs):
        """
        动态获取前一天的前十位热度搜索关键词
        """
        with manage_redis(self.DB, type(self)) as redis:
            date = datetime.datetime.today() - datetime.timedelta(1)
            return redis.zrevrange(self.heat_key(date), 0, 10)


history_redis = HistoryRedisOperation.choice_redis_db('search')
