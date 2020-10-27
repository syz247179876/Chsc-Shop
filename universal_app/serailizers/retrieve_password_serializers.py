# -*- coding: utf-8 -*-
# @Time  : 2020/10/13 下午7:47
# @Author : 司云中
# @File : retrieve_password_serializers.py
# @Software: Pycharm

from rest_framework import serializers
from django.utils.translation import ugettext as _

class RetrievePasswordSerializer(serializers.Serializer):
    """找回密码序列化器"""

    RETRIEVE_KEY = 'retrieve_key'

    RETRIEVE_WAY = (
        ('email', 'email'),
        ('phone', 'phone'),
    )


    def __init__(self):
        super().__init__()

        self.fields[self.RETRIEVE_KEY] = serializers.CharField(max_length=30, validators=[])
        self.fields['code'] = serializers.CharField(max_length=6)
        self.fields['way'] = serializers.ChoiceField(choices=self.RETRIEVE_WAY)


    def validate(self, attrs):
        key = self.redis.key('retrieve-pwd', attrs.get('way'), attrs.get(self.RETRIEVE_KEY))
        if self.redis.check_code(key, attrs.get('code')):
            return attrs
        raise serializers.ValidationError('验证码错误')

    @property
    def redis(self):
        return self.context.get('redis')



