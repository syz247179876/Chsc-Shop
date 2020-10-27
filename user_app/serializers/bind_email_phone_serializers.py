# -*- coding: utf-8 -*-
# @Time : 2020/7/27 11:26
# @Author : 司云中
# @File : bind_email_phone_serializers.py
# @Software: PyCharm
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from Emall.loggings import Logging
from user_app.utils.validators import DRFPhoneValidator

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')

User = get_user_model()

class BindPhoneOrEmailSerializer(serializers.Serializer):
    old_phone = serializers.CharField(required=False, validators=[DRFPhoneValidator()])
    phone = serializers.CharField(required=False,
                                  max_length=11,
                                  validators=[DRFPhoneValidator(), UniqueValidator(queryset=User.objects.all())]
                                  )
    old_email = serializers.EmailField(required=False)
    email = serializers.EmailField(required=False,
                                   validators=[UniqueValidator(queryset=User.objects.all())])
    code = serializers.CharField(required=True)
    is_existed = serializers.BooleanField()
    way = serializers.CharField()  # 绑定方式


    def validate_code(self, value):
        """验证码校验"""
        if len(value) != 6:
            raise serializers.ValidationError("验证码长度为6位")
        return value

    def validate_way(self, value):
        """绑定功能方式校验"""
        if value.lower() not in ['email', 'phone']:
            raise serializers.ValidationError("方式必须在email和phone中选择")
        return value

    def validate(self, attrs):
        """整体校验"""
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
