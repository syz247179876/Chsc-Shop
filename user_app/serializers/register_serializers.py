# -*- coding: utf-8 -*-
# @Time : 2020/7/30 11:26
# @Author : 司云中
# @File : register_serializers.py
# @Software: PyCharm
from user_app.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from user_app.utils.validators import DRFUsernameValidator, DRFPasswordValidator, DRFPhoneValidator


class RegisterSerializer(serializers.Serializer):
    """注册序列化器"""

    REGISTER_WAY = (
        ('email', 'email'),
        ('phone', 'phone'),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password'] = serializers.CharField(required=True, min_length=8, max_length=20, validators=[DRFPasswordValidator()])  # 密码
        self.fields['email'] = serializers.EmailField(required=False)
        self.fields['username'] = serializers.CharField(required=False, max_length=20, validators=[DRFUsernameValidator()])
        self.fields['phone'] = serializers.CharField(required=False, validators=[DRFPhoneValidator()])
        self.fields['code'] = serializers.CharField(max_length=6, required=True)  # 验证码
        self.fields['way'] = serializers.ChoiceField(choices=self.REGISTER_WAY)  # 登录方式

    def validate_code(self, value):
        """验证码校验"""
        if len(value) != 6:
            raise serializers.ValidationError("验证码位数不对")
        return value

    def validate(self, attrs):
        """前端传过来的数据中必须包含email和phone二者之一"""
        way = attrs.get('way')
        if way == 'phone':
            if attrs.get('email') or attrs.get('username'):
                raise serializers.ValidationError('手机号注册条件不满足或过多')
        elif way == 'email':
            if attrs.get('phone') or not attrs.get('username'):
                raise serializers.ValidationError('邮箱注册条件不满足或过多')
        return attrs









