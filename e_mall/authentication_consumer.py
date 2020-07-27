# -*- coding: utf-8 -*-
# @Time : 2020/5/8 18:37
# @Author : 司云中
# @File : authentication_consumer.py
# @Software: PyCharm


from User_app.models.user_models import Consumer
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q
import logging
from User_app import validators

common_log = logging.getLogger('django')


class EmailOrUsername(ModelBackend):
    """
    针对邮箱或者用户名登录，自定义认证
    用户名规则：6～20位，由数字，字母组成
    邮箱规则：正常邮箱规则
    """

    def authenticate(self, request=None, username=None, password=None, **kwargs):
        global consumer
        try:

            if validators.username_validate(username) or validators.email_validate(username):
                consumer = User.objects.get(Q(username=username) | Q(email=username))
            else:
                return None  # 用户名不正确
        except User.DoesNotExist:
            return None
        else:
            if consumer.check_password(password):
                return consumer
            return None  # 密码不正确


class Phone(ModelBackend):
    """
    针对手机用户认证
    手机号：正常手机号格式
    """

    def authenticate(self, request=None, username=None, password=None, **kwargs):
        """authenticate consumer, only phones are allowed to login"""
        global consumer
        try:
            if validators.phone_validate(username):
                consumer = Consumer.consumer_.get(phone=username)
            else:
                return None
        except Consumer.DoesNotExist:
            return None
        else:
            if consumer.check_password(password):
                return consumer
            return None


email_or_username = EmailOrUsername()
phone = Phone()
