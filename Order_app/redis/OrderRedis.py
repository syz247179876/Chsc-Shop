# -*- coding: utf-8 -*-
# @Time  : 2020/8/9 下午7:55
# @Author : 司云中
# @File : OrderRedis.py
# @Software: Pycharm
from e_mall.base_redis import BaseRedis


class RedisOrderOperation(BaseRedis):
    """the operation of Shopper about redis"""

    def __init__(self, redis_instance):
        super().__init__(redis_instance)
