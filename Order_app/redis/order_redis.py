# -*- coding: utf-8 -*-
# @Time  : 2020/8/9 下午7:55
# @Author : 司云中
# @File : order_redis.py
# @Software: Pycharm
from Order_app.serializers.order_serializers import OrderCreateSerializer
from e_mall.base_redis import BaseRedis, manager_redis


class RedisOrderOperation(BaseRedis):
    """the operation of Shopper about redis"""

    def __init__(self, redis_instance):
        super().__init__(redis_instance)

    def set_order_expiration(self, pk):
        """设置订单过期30min时间"""
        with manager_redis(self.db) as redis:
            key = OrderCreateSerializer.generate_orderid(pk)
            redis.setex(key, 3000, 1)
