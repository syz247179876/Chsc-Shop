# -*- coding: utf-8 -*-
# @Time : 2020/8/1 14:03
# @Author : 司云中
# @File : verification_serializers.py
# @Software: PyCharm
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator

from User_app.models.user_models import Consumer
from User_app.validators import DRFPhoneValidator
from e_mall.loggings import Logging
from rest_framework import serializers
from django.utils.translation import ugettext as _


class VerificationSerializer(serializers.Serializer):
    """验证码序列化器"""

    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False, validators=[DRFPhoneValidator()], max_length=11)
    way = serializers.CharField()

    def validate(self, attrs):
        """前端传过来的数据中必须包含email和phone二者之一"""
        way = attrs.get('way')
        # 只要邮箱验证或手机号验证二者成立一个就跳过
        if way == 'phone':
            new_phone = attrs.get('phone', None)
            if not new_phone:
                msg = _('手机号绑定必须填写手机号')
                raise serializers.ValidationError(msg)
        elif way == 'email':
            new_email = attrs.get('email', None)
            if not new_email:
                msg = _('邮箱绑定必须填写邮箱')
                raise serializers.ValidationError(msg)
        return attrs

    def validate_way(self, value):
        """登录/注册方式校验"""
        if value.lower() not in ['email', 'phone']:
            raise serializers.ValidationError("方式必须在email和phone中选择")

        return value


class VerificationModifyPwdSerializer(serializers.Serializer):
    """转为修改密码设置的手机验证序列化器"""

    phone = serializers.CharField(validators=[DRFPhoneValidator()], max_length=11)

