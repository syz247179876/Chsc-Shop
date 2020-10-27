# -*- coding: utf-8 -*- 
# @Time : 2020/5/30 10:38 
# @Author : 司云中 
# @File : shopcart_redis.py 
# @Software: PyCharm
import math

from shop_app.models.commodity_models import Commodity
from Emall.base_redis import BaseRedis
from Emall.loggings import Logging

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class ShopCartRedisOperation(BaseRedis):

    def __init__(self, redis_instance):
        super().__init__(redis_instance)

    def get_shop_cart_id_and_page(self, user_id, **data):
        """
        Retrieve all stores under current user's shopping cart from redis,
        and the goods stored in this shopping cart under these stores
        从redis中取出该用户购物车下的所有店铺，以及这些店铺下的存入的购物车商品

        list + zset结构
        :param user_id:用户id
        :param data:HttpRequest.GET数据
        :return: dict  key:include(store id),value: include(commodity list)
        """
        store_and_commodity = {}  # 商铺和商品映射
        commodity_and_counts = {}  # 商品和其对应的数量之间的映射
        commodity_and_price = {}  # 商品和其对应的数量乘积的总价格的映射
        try:
            limit = 3 if 'limit' not in data else int(data.get('page')[0])
            page = int(data.get('page')[0])
            start = (page - 1) * limit
            end = page * limit
            first_key = self.key('Cart', user_id, 'store')  # 用于存放用户购物车内商品所属的店铺，键
            store_counts = self.redis.llen(first_key)  # 购物车所含有的店铺总数，O(1)
            store_value_decode = [int(i.decode()) for i in self.redis.lrange(first_key, start, end)]  # 商铺id列表解码,O(N)

            for store in store_value_decode:
                commodity_id = []  # 该用户购物车下的每个商铺下的商品id
                second_key = self.key('Cart', user_id, store, 'counts')  # 用于存放用户购物车内每个商铺有关商品数量对应的商品id，键
                third_key = self.key('Cart', user_id, store, 'price')  # 用于存放用户购物车内每个商铺有关商品总价格对应的商品id，键
                # 取出购物车中每个商铺中对应全部的商品id,进行解码
                # 时间复杂度O(log(n)+m),分数为float型，需转, m为成员数量

                # TODO:重构添加    withscore=True,用pipe减小网络延迟
                counts_list = [int(value.decode()) for value in self.redis.zrevrange(second_key, 0, -1)]
                price_list = [int(value.decode()) for value in self.redis.zrevrange(third_key, 0, -1)]
                for value in counts_list:
                    commodity_and_counts[value] = float(self.redis.zscore(second_key, value))

                for value in price_list:
                    commodity_id.append(value)
                    commodity_and_price[value] = float(self.redis.zscore(third_key, value))

                store_and_commodity.setdefault(store, commodity_id)
            common_logger.info(store_and_commodity)

            page = math.ceil(store_counts / limit)
            return store_and_commodity, commodity_and_price, commodity_and_counts, page
        except Exception as e:
            consumer_logger.error(e)
            return None, None, 0

    def delete_one_good(self, user_id, **kwargs):
        """
        delete goods based on commodity_id and store_id from redis
        :param user_id:
        :param kwargs: 额外参数，包含store_id，good_id，counts
        :return:bool
        """
        if 'store_id' not in kwargs or 'good_id' not in kwargs:
            return False
        else:
            try:
                store_id = int(kwargs['store_id'])
                first_key = self.key('Cart', user_id, 'store')
                store_list = [int(i.decode()) for i in self.redis.lrange(first_key, 0, -1)]  # O(n)
                if store_id not in store_list:  # 如果该用户名下没有该商铺，则返回删除失败
                    return False
                else:
                    good_id = int(kwargs['good_id'])
                    second_key = self.key('Cart', user_id, store_id, 'counts')
                    third_key = self.key('Cart', user_id, store_id, 'price')
                    is_success = self.redis.zrem(second_key, good_id) and self.redis.zrem(third_key, good_id)  # O(1)
                    return True if is_success else False
            except Exception as e:
                consumer_logger.error(e)
                return False

    def edit_one_good(self, user_id, **kwargs):
        """
        edit the information of goods which stored in redis based on commodity_id and store_id and counts
        :param user_id:
        :param kwargs: 额外参数，包含store_id，good_id，way(add or minus)
        :return:bool
        """
        if 'store_id' not in kwargs or 'good_id' not in kwargs or 'way' not in kwargs:
            return False
        try:
            store_id = int(kwargs['store_id'])
            first_key = self.key('Cart', user_id, 'store')
            store_list = [int(i.decode()) for i in self.redis.lrange(first_key, 0, -1)]  # O(n)
            if store_id not in store_list:  # 如果该用户名下没有该商铺，则返回删除失败
                return False
            else:
                good_id = int(kwargs['good_id'])
                signal_good = Commodity.commodity_.get(pk=good_id)  # 查询当前商品的单价和打折情况
                signal_good_price = signal_good.price
                signal_good_discounts = signal_good.discounts
                second_key = self.key('Cart', user_id, store_id, 'counts')
                third_key = self.key('Cart', user_id, store_id, 'price')
                if kwargs['way'] == 'add':
                    self.redis.zincrby(second_key, 1, good_id)  # 对id为good_id的商品数量加1,O(1)
                    self.redis.zincrby(third_key, float(signal_good_discounts * signal_good_price),
                                       good_id)  # 对id为good_id的商品数量加上优惠价,O(1)
                elif kwargs['way'] == 'minus':
                    self.redis.zincrby(second_key, -1, good_id)
                    self.redis.zincrby(third_key, -(float(signal_good_discounts * signal_good_price)),
                                       good_id)
                # self.redis.zadd(third_key,
                #                 {good_id: float(signal_good_price * signal_good_discounts * int(kwargs['counts']))})
        except Exception as e:
            consumer_logger.error(e)
            return False
        else:
            return True
