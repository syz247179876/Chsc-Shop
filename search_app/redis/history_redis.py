# -*- coding: utf-8 -*-
# @Time  : 2020/11/14 下午7:37
# @Author : 司云中
# @File : history_redis.py
# @Software: Pycharm
import datetime
from time import time

from Emall.base_redis import BaseRedis, manager_redis
from search_app import signals
from user_app.redis.favorites_redis import RedisFavoritesOperation

def client_key(func):
    """获取client的key装饰器"""
    def decorate(self, sender, request, key, **kwargs):
        if sender is None:  # 如果用户未登录
            sender = BaseRedis.get_client_ip(request=request)  # 获取客户端IP
            func(self, sender, request, key, **kwargs)
    return decorate



class HistoryRedisOperation(BaseRedis):

    def __init__(self, db, redis):
        super().__init__(db, redis)
        self.connect()

    def connect(self):
        signals.record_search.connect(self.save_search, sender=None)

    @property
    def score(self):
        return int(time())


    def user_key(self, key):
        return f'user-{key}'

    @property
    def heat_key(self):
        date = datetime.datetime.today()
        return f'heat-{date.strftime("%Y-%m-%d")}'

    @client_key
    def save_search(self, sender, request, key, **kwargs):
        """
        记录某用户的浏览记录
        有效时间1个月
        """
        with manager_redis('search', type(self)) as redis:
            # 为每个用户维护一个搜索有序集合
            with redis.pipeline() as pipe:
                pipe.zadd(self.user_key(sender), {key:self.score})
                # 60*60*24*30 = 25920000 30天存活
                pipe.expire(sender, 25920000)
                pipe.zincrby(self.heat_key, 1, key) # 将该关键字添加到热搜有序集合中,如果存在key,则+1,不存在设置为1
                pipe.execute()

    @client_key
    def delete_search_single(self, sender, request, key, **kwargs):
        """
        单删某条搜索历史记录
        """
        with manager_redis('search', type(self)) as redis:
            redis.zrem(self.user_key(sender), key)

    @client_key
    def delete_search_all(self, sender, request, key, **kwargs):
        """
        群删所有搜索历史记录
        """
        with manager_redis('search', type(self)) as redis:
            redis.delete(self.user_key(sender))

    @client_key
    def retrieve_last_ten(self, sender, request, key, **kwargs):
        """获取最新的10条搜索记录"""

        # with 生存周期持续到函数结束
        with manager_redis('search', type(self)) as redis:
            page = kwargs.get('page')
            count = kwargs.get('count')
            result = redis.zrevrange(self.user_key(sender), page*count, (page+1)*count) # 返回分数从高到低的前十个(时间最近的前十个)
            return result

    def heat_search(self, sender, request, key, **kwargs):
        """
        每周热搜
        动态更新每日的前十位
        """
        with manager_redis('search', type(self)) as redis:
            result = redis.zrevrange(self.heat_key, 0, 10)  # 前十大热搜
            return result

    def timer_eliminate_heat(self, sender, request, key, **kwargs):
        """
        定时清空每周的热搜榜
        """
        pass


history_redis = HistoryRedisOperation.choice_redis_db('search')