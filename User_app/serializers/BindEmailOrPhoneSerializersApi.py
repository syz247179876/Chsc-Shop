# -*- coding: utf-8 -*-
# @Time : 2020/7/27 11:26
# @Author : 司云中
# @File : FavoritesSerializersApi.py
# @Software: PyCharm
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator

from User_app import validators
from User_app.models.user_models import Consumer
from User_app.validators import DRFPhoneValidator, DRFEmailValidator
from e_mall.loggings import Logging
from rest_framework import serializers
from django.utils.translation import ugettext as _

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class BindPhoneOrEmailSerializer(serializers.Serializer):
    old_phone = serializers.CharField(required=False, validators=[DRFPhoneValidator()])
    phone = serializers.CharField(required=False,
                                  max_length=11,
                                  validators=[DRFPhoneValidator(), UniqueValidator(queryset=Consumer.consumer_.all())]
                                  )
    old_email = serializers.EmailField(required=False)
    email = serializers.EmailField(required=False,
                                   validators=[UniqueValidator(queryset=User.objects.all())])
    code = serializers.CharField(required=True)
    is_existed = serializers.BooleanField()
    way = serializers.CharField()  # 绑定方式

    @staticmethod
    def bind_phone(cache, instance, validated_data):
        """改绑手机号"""
        is_existed = validated_data['is_existed']
        code = validated_data['code']
        new_phone = validated_data['phone']
        if is_existed:
            # 旧手机接受验证码
            old_phone = validated_data['old_phone']
            is_success = cache.check_code(old_phone, code)
        else:
            # 新手机中核对验证码
            is_success = cache.check_code(new_phone, code)
        if is_success:
            instance.phone = new_phone
            try:
                instance.save()
            except Exception as e:
                consumer_logger.error(e)
                return False
            else:
                return True
        return False

    @staticmethod
    def bind_email(cache, instance, validated_data):
        """改绑邮箱"""
        is_existed = validated_data['is_existed']
        code = validated_data['code']
        new_email = validated_data['email']
        if is_existed:
            # 旧邮箱接受验证码
            old_email = validated_data['old_email']
            is_success = cache.check_code(old_email, code)
        else:
            # 新邮箱中核对验证码
            is_success = cache.check_code(new_email, code)
        if is_success:
            instance.email = new_email
            try:
                instance.save()
            except Exception as e:
                consumer_logger.error(e)
                return False
            else:
                return True
        return False

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
