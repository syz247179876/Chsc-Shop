# -*- coding: utf-8 -*-
# @Time  : 2020/10/13 下午5:55
# @Author : 司云中
# @File : login_serializers.py
# @Software: Pycharm
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_jwt.compat import PasswordField, get_username_field, Serializer
from rest_framework_jwt.settings import api_settings
from django.utils.translation import ugettext as _
from User_app import validators
from e_mall.authentication_consumer import email_or_username, phone

User = get_user_model()
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class UserJwtLoginSerializer(Serializer):
    """
    用户登录验证
    """

    LOGIN_KEY = 'login_key'

    LOGIN_WAY = (
        ('username', 'username'),
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
            max_length=30
        )
        self.fields['password'] = PasswordField(write_only=True, required=False)
        self.fields['previous_page'] = serializers.CharField()  # 前一页url
        self.fields['code'] = serializers.CharField(max_length=6, required=False)  # 验证码
        self.fields['is_remember'] = serializers.BooleanField()  # 是否记住用户名
        self.fields['way'] = serializers.ChoiceField(choices=self.LOGIN_WAY)

    @property
    def username_field(self):
        """username字段名"""
        return get_username_field()

    # 对前端传入的属性字段进行验证
    def validate(self, attrs):

        # 获取字段
        user = None

        # 手机校验验证码
        if attrs.get('way') == 'phone' and not self.redis.check_code(attrs.get(self.LOGIN_KEY), attrs.get('code')):
            raise serializers.ValidationError('验证码不存在或错误')

        credentials = {
            attrs.get('way'): attrs.get(self.LOGIN_KEY),
            'password': attrs.get('password', 1),
            'code': attrs.get('code', 1),
            'way': attrs.get('way')
        }

        # 登录方式，邮箱或用户名,手机登录
        # 创建user对象
        if hasattr(self, credentials.get('way')):
            func = getattr(self, credentials.get('way'))
            user = func(**credentials)

        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise serializers.ValidationError(msg)

            payload = jwt_payload_handler(user)

            return {
                'token': jwt_encode_handler(payload),
                'user': user,
                'previous_page': validators.url_validate(attrs.get('previous_page')),
                'is_remember': attrs.get('is_remember'),
            }
        else:
            msg = _('Unable to log in with provided credentials.')
            raise serializers.ValidationError(msg)

    @property
    def redis(self):
        """获取视图实例"""
        return self.context.get('redis')

    def validate_code(self, value):
        """验证码校验"""
        if len(value) != 6:
            raise serializers.ValidationError("验证码为6位数")
        return value

    def email(self, **kwargs):
        return email_or_username.authenticate(**kwargs)

    def username(self, **kwargs):
        return email_or_username.authenticate(**kwargs)

    def phone(self, **kwargs):
        return phone.authenticate(**kwargs)

