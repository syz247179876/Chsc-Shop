# -*- coding: utf-8 -*-
# @Time  : 2021/2/15 下午8:28
# @Author : 司云中
# @File : role_serializers.py
# @Software: Pycharm
import time
import uuid

from rest_framework import serializers
from manager_app.models import ManagerRole


class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器"""

    permission = serializers.ListField(child=serializers.CharField(max_length=8), allow_empty=True, write_only=True)

    class Meta:
        model = ManagerRole
        fields = ('role_name', 'description', 'pid', 'permission')

    def add_role(self):
        """添加角色信息"""
        permission_list = self.validated_data.pop('permission')
        role = self.Meta.model.role_.create(**self.validated_data)
        role.add(*permission_list)

    def modify_role(self):
        """修改角色信息"""
        permission_list = self.validated_data.pop('permission')
        role = self.Meta.model.role_.update(**self.validated_data)
        role.set(permission_list)


class RoleDeleteSerializer(serializers.ModelSerializer):

    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)