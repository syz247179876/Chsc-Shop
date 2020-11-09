# -*- coding: utf-8 -*-
# @Time  : 2020/11/9 下午1:04
# @Author : 司云中
# @File : throttle.py
# @Software: Pycharm
from django.core.cache import caches
from rest_framework.throttling import UserRateThrottle


class PraiseRateThrottle(UserRateThrottle):
    """点赞/取消点赞限流"""
    scope = 'user-praise'
    cache = caches['remark']
