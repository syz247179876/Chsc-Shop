# -*- coding: utf-8 -*-
# @Time  : 2021/2/9 下午11:24
# @Author : 司云中
# @File : auth_serializers.py
# @Software: Pycharm
from django.contrib.auth import get_user_model
from django.db import transaction, DataError
from rest_framework import serializers

from Emall.exceptions import DataFormatError, SqlServerError
from manager_app.models import Managers

User = get_user_model()
class ManagerLoginSerializer(serializers.ModelSerializer):
    """
    后台登录序列化器
    """

    username = serializers.CharField(max_length=20, min_length=2)
    password = serializers.CharField(max_length=128)


class ManagerRegisterSerializer(serializers.ModelSerializer):
    """
    创建其他管理者序列化器
    """
    IDENTITY = {
        '0':'is_staff',
        '1':'is_super_manager'
    }

    # 用户名
    username = serializers.CharField(max_length=20, min_length=2)

    # 真实姓名
    full_name = serializers.CharField(max_length=10)

    # 身份
    identity = serializers.CharField(max_length=1)

    # 角色
    rid = serializers.IntegerField(min_value=1)


    def create_manager(self):
        identity = self.validated_data.pop('identity')
        rid = self.validated_data.pop('rid')
        if identity not in self.IDENTITY:
            raise DataFormatError()
        # 生成数据库所需字段
        credential = {
            self.IDENTITY[identity]:identity,
            'username': self.validated_data['username'],
            'full_name': self.validated_data['full_name'],
        }
        try:
            with transaction.atomic():
                user = User.objects.create(**credential) # 创建user对象
                Managers.manager_.create(user=user, role_id=rid)
        except DataError:
            raise SqlServerError()





