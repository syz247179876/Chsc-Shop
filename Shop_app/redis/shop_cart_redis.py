# -*- coding: utf-8 -*- 
# @Time : 2020/6/2 14:22 
# @Author : 司云中 
# @File : shop_redis.py 
# @Software: PyCharm
from Shop_app.models.commodity_models import Commodity
from User_app.redis.base_redis import BaseRedis
from e_mall.loggings import Logging

common_logger = Logging.logger('django')

trolley_ = Logging.logger('trolley_')


class ShopRedisCartOperation(BaseRedis):
    """the operation of shop cart about redis,it means add goods into shop cart"""

    def __init__(self, redis_instance):
        super().__init__(redis_instance)

    @staticmethod
    def get_commodity(goods_id):
        """retrieve good instance based on good_id(index)"""
        try:
            commodity = Commodity.commodity_.get(pk=goods_id)
        except Commodity.DoesNotExist:
            return None
        else:
            return commodity

    def add_goods_into_shop_cart(self, user_id, **kwargs):
        """add new shop into shop_cart"""
        if 'store_id' not in kwargs or 'goods_id' not in kwargs or 'counts' not in kwargs:
            # 防止纯接口攻击
            return False

        try:
            store_id = kwargs.get('store_id')
            goods_id = kwargs.get('goods_id')
            counts = kwargs.get('counts')
            first_key = self.key('Cart', user_id, 'store')  # 用于存放用户购物车内商品所属的店铺，键
            store_list = [int(value.decode()) for value in self.redis.lrange(first_key, 0, -1)]
            if store_id not in store_list:
                self.redis.lpush(first_key, store_id)
            second = self.key('Cart', user_id, store_id, 'counts')  # 数量 ,键
            third = self.key('Cart', user_id, store_id, 'price')  # 单价*数量 ,键
            self.redis.zadd(second, {goods_id: counts})  # 添加 商品id - 数量映射
            goods = self.get_commodity(goods_id)  # get instance of designative good
            self.redis.zadd(third, {goods_id: float(goods.price * goods.discounts)})  # 添加商品id  - 价格映射
        except Exception as e:
            trolley_.info(e)
            return False
        else:
            return True



