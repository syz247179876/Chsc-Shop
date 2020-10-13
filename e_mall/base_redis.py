# -*- coding: utf-8 -*-
# @Time : 2020/5/27 23:16
# @Author : 司云中
# @File : base_redis.py
# @Software: PyCharm
import contextlib

from django_redis import get_redis_connection
from e_mall.settings import REDIS_SECRET
from e_mall.loggings import Logging

common_logger = Logging.logger('django')


@contextlib.contextmanager
def manager_redis(db):
    try:
        redis = get_redis_connection(db)  # redis实例链接
        yield redis
    except Exception as e:
        common_logger.info(e)
        return None
    else:
        redis.close()


class BaseRedis:
    _instance = {}

    def __init__(self, db):
        self.db = db  # 选择配置中哪一种的数据库

    @classmethod
    def choice_redis_db(cls, db):
        """
        选择配置中指定的数据库
        单例模式，减小new实例的大量创建的次数，减少内存等资源的消耗（打开和关闭连接），共享同一个资源
        """

        if not cls._instance.setdefault(cls.__name__, None):
            cls._instance[cls.__name__] = cls(db)  # 自定义操作类实例
        return cls._instance[cls.__name__]

    @property
    def salt(self):
        return REDIS_SECRET

    @staticmethod
    def key(*args):
        """
        字符串拼接形成key
        :param args: 元祖依赖值
        :return: str
        """
        keywords = (str(value) if not isinstance(value, str) else value for value in args)
        # return make_password('-'.join(keywords), salt=self.salt)   # 加密贼耗时
        return '-'.join(keywords)

    def check_code(self, key, value):
        """
        检查value是否和redis中key映射的value对应？
        :param key: key in key
        :param value: value from outside
        :return: bool
        """
        with manager_redis(self.db) as redis:
            if redis is None:
                return False
            elif redis.exists(key):
                _value = redis.get(key).decode()
                return True if _value == value else False
            else:
                return False

    def save_code(self, key, code, time):
        """
        缓存验证码并存活 time（s）
        :param key: key of redis
        :param code: code from outside
        :param time: (second)
        :return: bool
        """

        with manager_redis(self.db) as redis:
            if redis is None:
                return False
            redis.setex(key, time, code)  # 原子操作，设置键和存活时间

    def get_ttl(self, key):
        """
        获取某个键的剩余过期时间
        键永久：-1
        键不存在：-2
        :param key: key of redis
        :return: int
        """
        with manager_redis(self.db) as redis:
            if redis is None:
                return False
            redis.ttl(key)
