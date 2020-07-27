# -*- coding: utf-8 -*-
# @Time : 2020/7/27 11:26
# @Author : 司云中
# @File : FavoritesSerializersApi.py
# @Software: PyCharm
from rest_framework.validators import UniqueValidator

from User_app import validators
from User_app.models.user_models import Consumer
from e_mall.loggings import Logging
from rest_framework import serializers
from django.utils.translation import ugettext as _

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class BindPhoneOrEmailSerializer(serializers.Serializer):
    old_phone = serializers.CharField(required=False)
    new_phone = serializers.CharField(required=True, validators=[UniqueValidator(queryset=Consumer.consumer_.all())])
    code = serializers.CharField(required=True)
    is_existed = serializers.BooleanField()
    way = serializers.CharField()  # 绑定方式

    @staticmethod
    def bind_phone(cache, instance, validated_data):
        """改绑手机号"""
        is_existed = validated_data['is_existed']
        code = validated_data['code']
        new_phone = validated_data['new_phone']
        old_phone = validated_data['old_phone']
        if is_existed:
            # 旧手机接受验证码
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
        new_email = validated_data['new_email']
        old_email = validated_data['old_email']
        if is_existed:
            # 旧邮箱接受验证码
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

    def validate(self, attrs):
        """重写验证方法"""
        new_field = attrs.get('new_field')
        # 只要邮箱验证或手机号验证二者成立一个就跳过
        if not validators.phone_validate(new_field) and not validators.email_validate(new_field):
            msg = _('Unable to validate phone with provided credentials.')
            raise serializers.ValidationError(msg)
        return {
            'code': attrs.get('code'),
            'new_field': new_field,
            'old_field': attrs.get('old_field'),
            'is_existed': attrs.get('is_existed')
        }
