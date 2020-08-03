# -*- coding: utf-8 -*-
# @Time : 2020/8/1 14:03
# @Author : 司云中
# @File : FootSerializerApi.py
# @Software: PyCharm
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator

from User_app.models.user_models import Consumer
from e_mall.loggings import Logging
from rest_framework import serializers


class VerificationSerializer(serializers.Serializer):
    """验证码序列化器"""

    email = serializers.EmailField(required=False, validators=[UniqueValidator(queryset=User.objects.all())])
    phone = serializers.CharField(required=False, validators=[UniqueValidator(queryset=Consumer.consumer_.all())])
    way = serializers.CharField()

    def validate(self, attrs):
        """前端传过来的数据中必须包含email和phone二者之一"""
        if attrs.get('email', None) and attrs.get('phone', None):
            raise serializers.ValidationError('不要耍小诡计～')
        return attrs

    def validate_way(self, value):
        """登录/注册方式校验"""
        if value.lower() not in ['email', 'phone']:
            raise serializers.ValidationError("方式必须在email和phone中选择")
        return value
