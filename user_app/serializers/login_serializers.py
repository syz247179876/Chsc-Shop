# -*- coding: utf-8 -*-
# @Time  : 2020/10/13 下午5:55
# @Author : 司云中
# @File : login_serializers.py
# @Software: Pycharm
from django.conf import settings
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework_jwt.compat import PasswordField, get_username_field, Serializer
from rest_framework_jwt.settings import api_settings

from Emall.authentication import email_or_username, phone
from Emall.exceptions import CodeError, UserForbiddenError, UserNotExists
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


class UserJwtLoginSerializer(Serializer):
    """
    用户登录验证
    """

    LOGIN_KEY = 'login_key'

    LOGIN_WAY = (
        ('email', 'email'),
        ('phone', 'phone'),
    )

    def __init__(self, *args, **kwargs):
        """
        Dynamically add the USERNAME_FIELD to self.fields.
        """
        super().__init__(*args, **kwargs)  # 先初始化

        # 动态根据model字段名向OrderDict中添加键
        # 唯一验证
        # 自定义验证
        self.fields[self.LOGIN_KEY] = serializers.CharField(
            max_length=20
        )
        self.fields['password'] = PasswordField(write_only=True, required=False, min_length=8, max_length=20)
        self.fields['next'] = serializers.URLField(required=False)  # 前一页url
        self.fields['code'] = serializers.CharField(max_length=6, required=False)  # 验证码
        self.fields['is_remember'] = serializers.BooleanField()  # 是否记住用户名
        self.fields['way'] = serializers.ChoiceField(choices=self.LOGIN_WAY)

    @property
    def username_field(self):
        """username字段名"""
        return get_username_field()

    def filter_credentials(self, **attrs):
        way = attrs.get('way')
        if way == 'phone':
            return {
                attrs.get('way'): attrs.get(self.LOGIN_KEY),
                'way': way
            }
        elif way in ['email', 'username']:
            return {
                attrs.get('way'): attrs.get(self.LOGIN_KEY),
                'password': attrs.get('password'),
                'way': way
            }

    # 对前端传入的属性字段进行验证
    def validate(self, attrs):

        # 获取字段
        user = None
        way = attrs.get('way')

        # 手机校验验证码
        if way == 'phone' and not self.redis.check_code(attrs.get(self.LOGIN_KEY), attrs.get('code')):
            raise CodeError()

        credentials = self.filter_credentials(**attrs)  # 过滤不同操作所需字段

        # 登录方式，邮箱或用户名,手机登录
        # 创建user对象
        if hasattr(self, credentials.get('way')):
            func = getattr(self, credentials.get('way'))
            user = func(**credentials)

        if user:
            if not user.is_active:
                raise UserForbiddenError()
            payload = jwt_payload_handler(user)

            return {
                'token': jwt_encode_handler(payload),
                'next': attrs.get('next') or settings.DEFAULT_REDIRECT_URI,
                # validators.url_validate(attrs.get('next'))
                'is_remember': attrs.get('is_remember'),
            }
        else:
            msg = _('用户不存在或密码不正确')
            raise UserNotExists(msg)

    @property
    def redis(self):
        """获取视图实例"""
        return self.context.get('redis')

    @staticmethod
    def validate_code(value):
        """验证码校验"""
        if len(value) != 6:
            raise serializers.ValidationError("验证码为6位数")
        return value

    @staticmethod
    def email(**kwargs):
        return email_or_username.authenticate(**kwargs)

    @staticmethod
    def username(**kwargs):
        return email_or_username.authenticate(**kwargs)

    @staticmethod
    def phone(**kwargs):
        return phone.authenticate(**kwargs)
