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

    def __init__(self, redis_instance):
        super().__init__(redis_instance)

    def check_code(self, key, value):
        """compare key-value code and code in redis for equality """
        try:
            common_logger.info(key)
            if self.redis.exists(key):
                _value = self.redis.get(key).decode()
                return True if _value == value else False
            else:
                return False
        except Exception as e:
            shopper_logger.error(e)
            return False
        finally:
            self.redis.close()

    def save_code(self, key, code, time):
        """cache verification code for ten minutes"""
        try:
            self.redis.set(key, code)
            self.redis.expire(key, time)
        except Exception as e:
            shopper_logger.error(e)
        finally:
            self.redis.close()
