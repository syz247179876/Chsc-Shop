# -*- coding: utf-8 -*- 
# @Time : 2020/5/28 15:56 
# @Author : 司云中 
# @File : foot_redis.py 
# @Software: PyCharm
import datetime
import math
import time

from e_mall.base_redis import BaseRedis
from e_mall.loggings import Logging

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class FootRedisOperation(BaseRedis):
    """the operation of historical footprints about redis"""

    def __init__(self, redis_instance):
        super().__init__(redis_instance)

    def get_time_scope(self, limit, page):
        """
        get limit scope of time in order to obtain the list of commodity_id regard with timestamp
        datetime --> str --> <class 'time.struct_time'>(tuple) -->timestamp
        """
        today = datetime.datetime.now()  # 以今天datetime为基础
        max_timedelta = datetime.timedelta(limit * (page - 1))
        min_timedelta = datetime.timedelta(limit * page)
        min_score = today - min_timedelta
        max_score = today - max_timedelta
        min_score_str = min_score.strftime("%Y-%m-%d %H:%M:%S")
        max_score_str = max_score.strftime("%Y-%m-%d %H:%M:%S")
        min_score_timestamp = int(time.mktime(time.strptime(min_score_str, "%Y-%m-%d %H:%M:%S")))  # 必须为time的strptime
        max_score_timestamp = int(time.mktime(time.strptime(max_score_str, "%Y-%m-%d %H:%M:%S")))
        return min_score_timestamp, max_score_timestamp

    def get_foot_commodity_id_and_page(self, user_id, **kwargs):
        """
        obtain limit list of commodity that stored in redis(use zset有序集合) to hit database
        :param user_id:用户id
        :param kwargs:request.data的Querydict实例
        :return:list
        """
        try:
            key = self.key('foot', user_id)
            limit = 2 if 'limit' not in kwargs else int(kwargs.get('limit')[0])
            page = int(kwargs.get('page')[0])
            min_score_timestamp, max_score_timestamp = self.get_time_scope(limit, page)
            foot_limit_list = self.redis.zrangebyscore(key, min_score_timestamp,
                                                       max_score_timestamp)  # 获取scope范围内的commodity_id
            foot_score_counts = self.redis.zcount(key, min_score_timestamp, max_score_timestamp)  # 获取scope范围内的总个数
            foot_total_counts = self.redis.zcard(key)  # 获取foot的总个数
            page = math.ceil(foot_total_counts/foot_score_counts)
            foot_limit_list_decode = [int(pk.decode()) for pk in foot_limit_list]  # decode
            return foot_limit_list_decode, page
        except Exception as e:
            consumer_logger.error(e)
            return None, 0
        finally:
            self.redis.close()

    def add_foot_commodity_id(self, user_id, **kwargs):
        """
        get id of commodity when consumer browse a product
        :param user_id:用户id
        :param kwargs:request.data的Querydict实例
        :return:boolean
        """
        try:
            key = self.key('foot', user_id)
            timestamp = int(time.time())  # 毫秒级别的时间戳
            commodity_id = int(kwargs.get('commodity_id'))
            self.redis.zadd(key, {commodity_id: timestamp})  # 分别表示用户id（加密），时间戳（分数值），商品id
            # 每个用户最多缓存100条历史记录
            if self.redis.zcard(key) == 100:
                self.redis.zremrangebyrank(key, 0, 0)  # 移除时间最早的那条记录
        except Exception as e:
            consumer_logger.error(e)
            return False
        else:
            return True
        finally:
            self.redis.close()

    def delete_foot_commodity_id(self, user_id, **kwargs):
        """
        delete one or all of id of commodity when consumer intend to eliminate his(her) historical footprints
        :param user_id:用户id
        :param kwargs:request.data的Querydict实例
        :return:boolean
        """
        try:
            key = self.key('foot', user_id)
            if 'is_all' not in kwargs:
                commodity_id = int(kwargs.get('commodity_id'))
                delete_counts = self.redis.zrem(key, commodity_id)  # 移除zset中某商品号元素
            else:
                delete_counts = self.redis.delete(key)
            return True if delete_counts else False
        except Exception as e:
            consumer_logger.error(e)
            return False
        finally:
            self.redis.close()
