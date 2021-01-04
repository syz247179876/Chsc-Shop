# -*- coding: utf-8 -*-
# @Time : 2020/5/8 18:37
# @Author : 司云中
# @File : authentication_consumer.py
# @Software: PyCharm

import logging
import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from user_app.utils import validators

common_log = logging.getLogger('django')
User = get_user_model()

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
            kwargs.pop('way')
            password = kwargs.pop('password')
            user = User.objects.get(**kwargs)
            user.last_login=datetime.datetime.today()
            user.save()
        except User.DoesNotExist: # 用户不存在
            return None
        else:                     # 密码错误
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
            phone = kwargs.get('phone')
            if validators.phone_validate(phone):
                user = User.objects.get(phone=phone)
                user.last_login=datetime.datetime.today()
                user.save()
            return user
        except User.DoesNotExist:
            return None


email_or_username = EmailOrUsername()
phone = Phone()
