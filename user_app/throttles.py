# -*- coding: utf-8 -*- 
# @Time : 2020/5/14 22:59 
# @Author : 司云中 
# @File : throttles.py 
# @Software: PyCharm
from django.core.cache import caches
from rest_framework.throttling import UserRateThrottle


class RedisThrottle(UserRateThrottle):
    """The base throttle which choice redis as cache"""
    cache = caches['redis']


class LoginThrottle(RedisThrottle):
    """Being used to restrict login"""
    scope = 'login'


class RegisterThrottle(RedisThrottle):
    """Being used to restrict register"""
    scope = 'register'


class ModifyPasswordThrottle(RedisThrottle):
    """Being used to restrict modify password"""
    caches = 'modify_password'


