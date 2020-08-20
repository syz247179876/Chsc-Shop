# -*- coding: utf-8 -*- 
# @Time : 2020/5/27 21:40 
# @Author : 司云中 
# @File : favorites_redis.py 
# @Software: PyCharm
import datetime
import math
import time
from User_app.models.user_models import Collection
from e_mall.base_redis import BaseRedis
from User_app.views.tasks import format_data
from e_mall.loggings import Logging


common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class RedisFavoritesOperation(BaseRedis):
    """the operation of Favorites about redis"""

    def __init__(self, redis_instance):
        super().__init__(redis_instance)


    def get_resultSet(self, user, page, page_size, **kwargs):
        """
        考虑缓存击穿：即使空结果集也放到缓存中去
        redis使用有序集合+hash表+List实现数据存储和获取
        确保有序，使用有序集合，在redis层面提升排序性能
        return: list（读取redis)， 查询集（读取mysql）
        """
        key = self.key('favorites', user.pk)  # 集合键
        commodity_dict = {int(name.decode()): score for name, score in
                          self.redis.zrevrange(key, (page-1)*page_size, page*page_size,  withscores=True)}
        if commodity_dict:   # 缓存命中,寻找对应的商品hash表
            list_resultSet = []
            for key in commodity_dict.keys():
                if key == 0:   # 如果数据库未命中，缓存中的0代表空数据
                    return list_resultSet
                hash_key = self.key('favorites', user.pk, key)
                offset, hresult = self.redis.hscan(hash_key)
                if offset != 0:
                    hresult.update(self.redis.hscan(hash_key,cursor=offset))   # 从上一次的offset中读取,防止hscan一次性没读完
                list_resultSet.append(hresult)
            # list扔到任务队列中去将字典中的bytes-->str,解析，转换成我需要的数据格式
            list_result_format = format_data.apply_async(args=(list_resultSet,))
            return list_result_format

        try:                 # 为命中缓存
            queryset = Collection.collection_.select_related('user').prefetch_related('commodity').filter(user=user)[(page-1)*page_size : page*page_size]
            pipe_two = self.redis.pipeline()  # 建立管道
            if queryset:   # 存在查询集
                for query in queryset:
                    timestamp = time.mktime(query.time.timetuple())
                    pipe_two.zadd(key, {query.pk:timestamp})
            else:
                pipe_two.zadd(key, {0:time.mktime(datetime.datetime.now().timetuple())})  # 添加0，防止缓存击穿
            pipe_two.expire(key, 30)  # 为每个有序集合设置30s的TTL
            pipe_two.execute()
            return queryset
        except Exception as e:
            consumer_logger.error(e)
            return None


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


