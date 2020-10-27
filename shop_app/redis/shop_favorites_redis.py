# -*- coding: utf-8 -*- 
# @Time : 2020/6/2 20:04 
# @Author : 司云中 
# @File : shop_favorites_redis.py 
# @Software: PyCharm
from Emall.base_redis import BaseRedis
from Emall.loggings import Logging

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class ShopRedisFavoritesOperation(BaseRedis):
    """the operation of shop cart about redis , it means add goods into favorites"""

    def __init__(self, db):
        super().__init__(db)

    def add_goods_into_favorites(self, user_id, **kwargs):
        """
           add id of goods which in favorites into redis
           :param user_id: 用户id
           :param data: request.data的Querydict实例
           :return: 是否添加成功
       """

        if 'goods_id' not in kwargs:
            return False
        try:
            key = self.key('favorites', user_id)
            commodity_id = int(kwargs.get('goods_id'))
            self.redis.lpush(key, commodity_id)  # add into list
        except Exception as e:
            consumer_logger.error(e)
            return False
        else:
            return True
        finally:
            self.redis.close()
