# -*- coding: utf-8 -*-
# @Time  : 2020/11/21 上午9:15
# @Author : 司云中
# @File : oauth_serializer.py
# @Software: Pycharm
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_jwt.settings import api_settings

from user_app.utils.validators import DRFPhoneValidator, DRFPasswordValidator

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
User = get_user_model()


def jwt_response_payload_handler(**kwargs):
    data = {key: value for key, value in kwargs.items()}
    return data


def generate_token(user, next):
    """生成token"""
    payload = jwt_payload_handler(user)  # 返回payload
    token = jwt_encode_handler(payload)  # 加密形成token
    response_data = jwt_response_payload_handler(token=token, next=next)
    return response_data


class QQOauthSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['access_token'] = serializers.CharField(max_length=128)
        self.fields['phone'] = serializers.CharField(max_length=11, validators=[DRFPhoneValidator(), UniqueValidator(
            queryset=User.objects.all())])
        self.fields['code'] = serializers.CharField(max_length=6)
        self.fields['password'] = serializers.CharField(required=True, max_length=20,
                                                        validators=[DRFPasswordValidator()])  # 密码
        self.fields['next'] = serializers.URLField(max_length=128)

    def validate_code(self, value):
        """验证码校验"""
        if len(value) != 6:
            raise serializers.ValidationError("验证码位数不对")
        return value
