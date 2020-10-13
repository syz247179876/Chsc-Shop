# -*- coding: utf-8 -*- 
# @Time : 2020/6/1 23:31 
# @Author : 司云中 
# @File : shopper_redis.py 
# @Software: PyCharm

from e_mall.base_redis import BaseRedis
from e_mall.loggings import Logging

common_logger = Logging.logger('django')

shopper_logger = Logging.logger('shopper_')


class RedisShopperOperation(BaseRedis):
    """the operation of Shopper about redis"""

    def __init__(self, db):
        super().__init__(db)

