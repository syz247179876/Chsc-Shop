# -*- coding: utf-8 -*- 
# @Time : 2020/5/28 15:56 
# @Author : 司云中 
# @File : foot_redis.py 
# @Software: PyCharm
import datetime
import time

from Emall.base_redis import BaseRedis, manage_redis
from Emall.exceptions import RedisOperationError
from Emall.loggings import Logging

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class FootRedisOperation(BaseRedis):
    """the operation of historical footprints about redis"""

    def __init__(self, db, redis):
        super().__init__(db, redis)

    '''
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
    '''

    @property
    def score(self):
        """
        设置足迹有序集合中对应键的分数值
        202101071610024776
        """

        return int('%s%d' % (''.join(datetime.datetime.now().strftime('%Y-%m-%d').split('-')), int(time.time())))

    def get_foot_commodity_id_and_page(self, user_id, **kwargs):
        """
        obtain limit list of commodity that stored in redis(use zset有序集合) to hit database
        :param user_id:用户id
        :param kwargs:request.data的Querydict实例
        :return:Dict
        """
        with manage_redis(self.db) as redis:
            try:
                key = self.key('foot', user_id)
                page = kwargs.get('page', 1)
                count = kwargs.get('page_size')
                # zrevrange 返回 [(name,score),...]
                commodity_dict = {int(name): score for name, score in
                                  redis.zrevrange(key, (page - 1) * count, page * count, withscores=True)}
                return commodity_dict
            except Exception as e:
                consumer_logger.error(e)
                raise RedisOperationError()

    def add_foot_commodity_id(self, user_id, validated_data):
        """
        消费者浏览某个商品，添加足迹
        :param validated_data: 验证后的数据
        :param user_id:用户id
        :return:boolean
        """
        # add_foot.apply_async(args=(pickle.dumps(self), user_id, validated_data))  # can't pickle _thread.lock objects
        with manage_redis(self.db) as redis:
            try:
                key = self.key('foot', user_id)
                timestamp = self.score  # 毫秒级别的时间戳
                commodity_id = validated_data['pk']
                # pipe = self.redis.pipeline()  # 添加管道，减少客户端和服务端之间的TCP包传输次数
                redis.zadd(key, {commodity_id: timestamp})  # 分别表示用户id（加密），当前日期+时间戳（分数值），商品id
                # 每个用户最多记录100条历史记录
                if redis.zcard(key) >= 100:  # 集合中key为键的数量
                    redis.zremrangebyrank(key, 0, 0)  # 移除时间最早的那条记录
                # pipe.execute()
            except Exception as e:
                consumer_logger.error(e)
                raise RedisOperationError()

    def delete_foot_commodity_id(self, user_id, **kwargs):
        """
        删除用户单/多条浏览记录
        :param user_id:用户id
        :param kwargs:request.data的Querydict实例
        :return:boolean
        """
        with manage_redis(self.db) as redis:
            try:
                key = self.key('foot', user_id)
                if kwargs.get('is_all', None):  # 是否删除所有足迹
                    redis.delete(key)  # 删除全部的记录
                else:
                    commodity_id = kwargs.get('commodity_id')
                    redis.zrem(key, commodity_id)  # 移除zset中某商品号元素
            except Exception as e:
                consumer_logger.error(e)
                raise RedisOperationError()
