# -*- coding: utf-8 -*-
# @Time : 2020/8/1 14:03
# @Author : 司云中
# @File : verification_serializers.py
# @Software: PyCharm
from django.contrib.auth.models import User

from user_app.models import Consumer
from user_app.utils.validators import DRFPhoneValidator
from rest_framework import serializers
from django.utils.translation import ugettext as _


class VerificationSerializer(serializers.Serializer):
    """验证码序列化器"""

    CHOICE_WAY = (
        ('email','email'),
        ('phone','phone')
    )

    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False, validators=[DRFPhoneValidator()], max_length=11)
    way = serializers.ChoiceField(choices=CHOICE_WAY)

    def validate(self, attrs):
        """前端传过来的数据中必须包含email和phone二者之一"""
        way = attrs.get('way')
        # 只要邮箱验证或手机号验证二者成立一个就跳过
        if way == 'phone':
            phone = attrs.get('phone', None)
            if not phone:
                msg = _('手机号验证码，必须填写手机号')
                raise serializers.ValidationError(msg)
        elif way == 'email':
            email = attrs.get('email', None)
            if not email:
                msg = _('邮箱验证码，必须填写邮箱')
                raise serializers.ValidationError(msg)
        return attrs


class PhoneOnlySerializer(serializers.Serializer):
    CHOICE_WAY = (
        ('phone', 'phone'),
    )
    phone = serializers.CharField(validators=[DRFPhoneValidator()], max_length=11)
    way = serializers.ChoiceField(choices=CHOICE_WAY)


class RetrieveCodeSerializer(VerificationSerializer):
    """找回密码序列化器"""


    def validate(self, attrs):
        """在基类验证函数基础在进一步验证"""
        credentials = super().validate(attrs)
        func = getattr(self, credentials.get('way'))
        func(**credentials)
        return attrs

    def email(self, **kwargs):
        """验证邮箱"""
        try:
            User.objects.get(email=kwargs.pop('email'))
        except User.DoesNotExist:
            raise serializers.ValidationError('邮箱不存在')


    def phone(self, **kwargs):
        """验证手机"""
        try:
            Consumer.consumer_.get(phone=kwargs.pop('phone'))
        except Consumer.DoesNotExist:
            raise serializers.ValidationError('手机号不存在')








class VerificationModifyPwdSerializer(serializers.Serializer):
    """转为修改密码设置的手机验证序列化器"""

    phone = serializers.CharField(validators=[DRFPhoneValidator()], max_length=11)

