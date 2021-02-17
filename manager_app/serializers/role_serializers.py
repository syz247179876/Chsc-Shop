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
        fields = ('role_name', 'description', 'pid')

    def add_role(self):
        self.Meta.model.role_.create(**self.validated_data)

    def modify_role(self):
        self.Meta.model.role_.update(**self.validated_data)
