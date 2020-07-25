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
        """choice designated db in redis"""
        """different redis db , but follow the single mode"""
        if not cls._instance.setdefault(db, None):
            cls._instance[db] = get_redis_connection(db)
        return cls(cls._instance[db])

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
