# -*- coding: utf-8 -*-
# @Time  : 2021/5/3 下午2:53
# @Author : 司云中
# @File : menu_serializers.py
# @Software: Pycharm

from rest_framework import serializers

from seller_app.models import Seller
from universal_app.models import Role, Permission


class SellerPermissionSerializer(serializers.ModelSerializer):

    child = serializers.SerializerMethodField()

    def get_child(self, obj):
        """对自身递归嵌套查询"""
        return SellerPermissionSerializer(instance=self.Meta.model.objects.filter(pre_id=obj.pk), many=True).data

    class Meta:
        model = Permission
        fields = ('pk', 'name', 'pid', 'child')


class SellerRoleSerializer(serializers.ModelSerializer):
    # 会采用内连接方式，将permission表与第三张表内连接进行查询
    permission = SellerPermissionSerializer(many=True)

    class Meta:
        model = Role
        fields = ('pk', 'role_name', 'rid', 'permission')


class SellerMenuSerializer(serializers.ModelSerializer):
    role = SellerRoleSerializer()

    class Meta:
        model = Seller
        fields = ('role',)
