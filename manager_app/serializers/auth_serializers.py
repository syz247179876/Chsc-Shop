# -*- coding: utf-8 -*-
# @Time  : 2021/2/9 下午11:24
# @Author : 司云中
# @File : auth_serializers.py
# @Software: Pycharm

from rest_framework import serializers
class ManagerLoginSerializer(serializers.ModelSerializer):
    """
    管理员序列化器
    """

    username = serializers.CharField(max_length=15, min_length=2, required=True)
    password = serializers.CharField(max_length=128, required=True)


