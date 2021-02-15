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
        extra_kwargs = {'pid': {'read_only': True}}

    def add_role(self):
        credential = self.validated_data
        pid = str(time.time() * 1000000)[4:12]
        credential['pid'] = pid
        self.Meta.model.role_.create(**credential)

    def modify_role(self):
        self.Meta.model.role_.update(**self.validated_data)
