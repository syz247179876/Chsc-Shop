# -*- coding: utf-8 -*-
# @Time  : 2020/8/9 下午7:55
# @Author : 司云中
# @File : order_redis.py
# @Software: Pycharm
from order_app.serializers.order_serializers import OrderCreateSerializer
from Emall.base_redis import BaseRedis, manage_redis


class RedisOrderOperation(BaseRedis):
    """the operation of Shopper about redis"""

    def __init__(self, db, redis):
        super().__init__(db, redis)

    def set_order_expiration(self, pk):
        """设置订单过期30min时间"""
        with manage_redis(self.db) as redis:
            key = OrderCreateSerializer.generate_orderid(pk)
            redis.setex(key, 3000, 1)
