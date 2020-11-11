# -*- coding: utf-8 -*- 
# @Time : 2020/6/1 23:31 
# @Author : 司云中 
# @File : seller_redis.py
# @Software: PyCharm

from Emall.base_redis import BaseRedis
from Emall.loggings import Logging

common_logger = Logging.logger('django')

shopper_logger = Logging.logger('shopper_')


class RedisShopperOperation(BaseRedis):
    """the operation of Shopper about redis"""

    def __init__(self, db, redis):
        super().__init__(db, redis)

