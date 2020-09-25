# -*- coding: utf-8 -*-
# @Time  : 2020/8/9 下午7:55
# @Author : 司云中
# @File : OrderRedis.py
# @Software: Pycharm
from Order_app.serializers.order_serializers import OrderCreateSerializer
from e_mall.base_redis import BaseRedis


class RedisOrderOperation(BaseRedis):
    """the operation of Shopper about redis"""

    def __init__(self, redis_instance):
        super().__init__(redis_instance)

    def set_order_expiration(self, pk):
        """设置订单过期时间"""
        key = OrderCreateSerializer.generate_orderid(pk)
        time = 900  # 900s=15min
        self.redis.setex(key, 3000, 1)
