# -*- coding: utf-8 -*-
# @Time : 2020/5/27 23:16
# @Author : 司云中
# @File : base_redis.py
# @Software: PyCharm
from django.contrib.auth.hashers import make_password
from django_redis import get_redis_connection


class BaseRedis:
    _instance = {}

    def __init__(self, redis_instance):
        self._redis = redis_instance

    @classmethod
    def choice_redis_db(cls, db):
        """选择不同的缓存，例如redis或memcached，甚至redis中不同的db"""
        """单例模式"""
        if not cls._instance.setdefault(db, None):
            cls._instance[db] = cls(get_redis_connection(db))
        return cls._instance[db]

    @property
    def redis(self):
        return self._redis

    @property
    def salt(self):
        """盐:上线改为随机生成(16位)"""
        return 'qq:247179876@qq.com,blog:syzzjw.cn'

    def key(self, *args):
        """
        对键加密
        非str转为str
        object类型要求定义__str__或__repr__方法
        """
        keywords = (str(value) if not isinstance(value, str) else value for value in args)
        return make_password('-'.join(keywords), salt=self.salt)
