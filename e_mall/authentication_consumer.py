# -*- coding: utf-8 -*-
# @Time : 2020/5/8 18:37
# @Author : 司云中
# @File : authentication_consumer.py
# @Software: PyCharm


import logging

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

from User_app import validators
from User_app.redis.user_redis import RedisUserOperation

common_log = logging.getLogger('django')


class EmailOrUsername(ModelBackend):
    """
    针对邮箱或者用户名登录，自定义认证
    用户名规则：6～20位，由数字，字母组成
    邮箱规则：正常邮箱规则
    """

    def authenticate(self, request=None, user=None, **kwargs):
        """
        根据传过来的不同key-value反射调用验证函数，以及根据不同key-value动态查询满足要求的user对象
        :param request: 请求对象
        :param user: 避免全局引用的user
        :param kwargs: 包含'email/username' 和 'password'
        :return: user对象 or None
        """
        try:
            password = kwargs.pop('password')
            query_fields = {}  # 存放查询字段
            validators_result = []
            for key, value in kwargs.items(): # 验证数据
                func_name = '{key}_validate'.format(key=key)
                if hasattr(validators, func_name):
                    func = getattr(validators,func_name)
                    validators_result.append(func(value))
                    query_fields.update({key:value})

            if len(validators_result):
                user = User.objects.get(**query_fields)
            else:
                return None
        except User.DoesNotExist:
            return None
        else:
            return user if user.check_password(password) else None


class Phone(ModelBackend):
    """
    针对手机用户认证(手机+验证码）
    """

    def authenticate(self, request=None, user=None, **kwargs):
        """
        :param request: request对象
        :return: user对象
        """
        try:
            code = kwargs.get('code')
            phone = kwargs.get('phone')
            if validators.phone_validate(phone):
                user = User.objects.select_related('consumer').get(consumer__phone=phone)
        except user.DoesNotExist:
            return None
        else:
            redis = RedisUserOperation.choice_redis_db('redis')
            key = redis.key('authentication', phone)
            return user if redis.check_code(key, code) else None


email_or_username = EmailOrUsername()
phone = Phone()
