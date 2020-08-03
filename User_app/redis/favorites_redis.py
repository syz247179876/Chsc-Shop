# -*- coding: utf-8 -*- 
# @Time : 2020/5/27 21:40 
# @Author : 司云中 
# @File : favorites_redis.py 
# @Software: PyCharm
import math

from e_mall.base_redis import BaseRedis

from e_mall.loggings import Logging


common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class RedisFavoritesOperation(BaseRedis):
    """the operation of Favorites about redis"""

    def __init__(self, redis_instance):
        super().__init__(redis_instance)

    def get_favorites_goods_id_and_page(self, user_id, **kwargs):
        """
        get id of goods which in favorites in redis(use list type) to hit database
        :param user_id: 用户id
        :param limit: 每次请求的limit大小
        :param page: 当前页
        :return:该用户limit内的商品id集合，和收藏夹中所具备的所有商品的个数
        """
        try:
            key = self.key('favorites', user_id)
            limit = 5 if 'limit' not in kwargs else int(kwargs.get('limit')[0])
            cur_page = int(kwargs.get('page')[0])
            start = (cur_page - 1) * limit
            end = cur_page * limit
            # the limit commodity_id of list
            favorites_limit_list_decode = [int(pk.decode()) for pk in self.redis.lrange(key, start, end)]
            favorites_total_counts = self.redis.llen(key)  # the length of list,need not decode
            page = math.ceil(favorites_total_counts / limit)
            return favorites_limit_list_decode, page
        except Exception as e:
            consumer_logger.error(e)
            return None, 0
        finally:
            self.redis.close()

    def delete_favorites_goods_id(self, user_id, **data):
        """
        delete id of goods which in favorites into redis
        :param user_id: 商品id
        :param data: request.data的Querydict实例
        :return:是否删除成功
        """
        try:
            key = self.key('favorites', user_id)
            if 'is_all' not in data:
                commodity_id = int(data.get('commodity_id')[0])
                delete_counts = self.redis.lrem(key, commodity_id)  # delete commodity_id from the list once
            else:
                delete_counts = self.redis.delete(key)  # delete this key
            return True if delete_counts else False
        except Exception as e:
            consumer_logger.error(e)
            return False
        finally:
            self.redis.close()


