# -*- coding: utf-8 -*-
# @Time  : 2021/2/15 下午2:40
# @Author : 司云中
# @File : permission_serializers.py
# @Software: Pycharm
from rest_framework import serializers

from manager_app.models import ManagerPermission


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerPermission
        fields = ('name', 'pid')
