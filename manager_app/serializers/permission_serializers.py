# -*- coding: utf-8 -*-
# @Time  : 2021/2/15 下午2:40
# @Author : 司云中
# @File : permission_serializers.py
# @Software: Pycharm
import time

from rest_framework import serializers

from manager_app.models import ManagerPermission


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ManagerPermission
        fields = ('name', 'description', 'pid')

    def create_permission(self):
        self.Meta.model.manager_permission_.create(**self.validated_data)

    def update_permission(self):
        self.Meta.model.manager_permission_.update(**self.validated_data)



