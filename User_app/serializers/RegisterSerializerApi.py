# -*- coding: utf-8 -*-
# @Time : 2020/7/30 11:26
# @Author : 司云中
# @File : RegisterSerializerApi.py
# @Software: PyCharm
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from User_app.models.user_models import Consumer
from User_app.validators import DRFUsernameValidator, DRFPasswordValidator


class RegisterSerializer(serializers.Serializer):
    """注册序列化器"""
    username = serializers.CharField(max_length=30,
                                     validators=[DRFUsernameValidator(), UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(max_length=20, validators=[DRFPasswordValidator()])  # 密码
    email = serializers.EmailField(required=False, validators=[UniqueValidator(queryset=User.objects.all())])
    phone = serializers.CharField(required=False, validators=[UniqueValidator(queryset=Consumer.consumer_.all())])

    code = serializers.CharField(max_length=6)  # 验证码
    way = serializers.CharField()  # 登录方式

    def validate_way(self, value):
        """登录/注册方式校验"""
        if value.lower() not in ['email', 'phone']:
            raise serializers.ValidationError("方式必须在email和phone中选择")
        return value

    def validate_code(self, value):
        """验证码校验"""
        if len(value) != 6:
            raise serializers.ValidationError("验证码长度为6位")
        return value

    def validate(self, attrs):
        """前端传过来的数据中必须包含email和phone二者之一"""
        if attrs.get('email', None) and attrs.get('phone', None):
            raise serializers.ValidationError('不要耍小诡计～')
        return attrs





