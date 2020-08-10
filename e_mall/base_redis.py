# -*- coding: utf-8 -*-
# @Time : 2020/5/27 23:16
# @Author : 司云中
# @File : base_redis.py
# @Software: PyCharm
from django.contrib.auth.hashers import make_password
from django_redis import get_redis_connection
from e_mall.loggings import Logging

common_logger = Logging.logger('django')


class BaseRedis:
    _redis_instances = {}
    _instance = {}

    def __init__(self, redis_instance):
        self._redis = redis_instance

    @classmethod
    def choice_redis_db(cls, db):
        """
        选择配置中指定的数据库
        单例模式，减小new实例的大量创建的次数，减少内存等资源的消耗（打开和关闭连接），共享同一个资源
        实现每个类实例对应一个redis实例
        """
        if not cls._instance.setdefault(cls.__name__, None):
            cls._redis_instances[db] = get_redis_connection(db)  # redis实例
            cls._instance[cls.__name__] = cls(cls._redis_instances[db])  # 自定义操作类实例
        return cls._instance[cls.__name__]

    @property
    def redis(self):
        return self._redis

    @property
    def salt(self):
        return 'qq:247179876@qq.com,blog:syzzjw.cn'

    def key(self, *args):
        """encryption , if param in args not str , convert into str"""
        keywords = (str(value) if not isinstance(value, str) else value for value in args)
        return make_password('-'.join(keywords), salt=self.salt)

    def check_code(self, key, value):
        """compare key-value code and code in redis for equality """
        try:
            if self.redis.exists(key):
                _value = self.redis.get(key).decode()
                return True if _value == value else False
            else:
                return False
        except Exception as e:
            common_logger.info(e)
        finally:
            self.redis.close()

    def save_code(self, key, code, time):
        """cache verification code for ten minutes"""
        try:
            self.redis.setex(key, time, code)  # 原子操作，设置键和存活时间
        except Exception as e:
            common_logger.info(e)
        finally:
            self.redis.close()

    def get_ttl(self, key):
        """
        获取某个键的剩余过期时间
        键永久：-1
        键不存在：-2
        """
        return self.redis.ttl(key)
