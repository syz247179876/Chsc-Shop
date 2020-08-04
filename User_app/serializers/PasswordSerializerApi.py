# -*- coding: utf-8 -*-
# @Time  : 2020/8/4 下午10:10
# @Author : 司云中
# @File : PasswordSerializerApi.py
# @Software: Pycharm


from rest_framework import serializers

from User_app.validators import DRFPasswordValidator


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=20, validators=[DRFPasswordValidator()])
    old_password = serializers.CharField(max_length=20, validators=[DRFPasswordValidator()])
    code = serializers.CharField(max_length=6)  # 验证码

    def validate_code(self, value):
        """验证码校验"""
        if len(value) != 6:
            raise serializers.ValidationError("验证码长度为6位")
        return value