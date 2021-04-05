# -*- coding: utf-8 -*-
# @Time  : 2021/2/15 下午2:40
# @Author : 司云中
# @File : permission_serializers.py
# @Software: Pycharm
import time

from rest_framework import serializers

from Emall.drf_validators import ModelIdExist
from Emall.exceptions import DataNotExist, DataFormatError
from seller_app.models import Seller
from universal_app.models import Permission, Role


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('pk', 'name', 'description', 'pid')
        read_only_fields = ('pk',)

    def create_permission(self):
        """添加权限"""
        credential = self.get_credential
        self.Meta.model.objects.create(**credential)

    def update_permission(self):
        """修改权限"""
        pk = self.context.get('request').data.get('pk')
        credential = self.get_credential
        self.Meta.model.objects.filter(pk=pk).update(**credential)

    @property
    def get_credential(self):
        return {
            'name': self.validated_data.pop('name'),
            'description': self.validated_data.pop('description'),
            'pid': self.validated_data.pop('pid')
        }


class PermissionDeleteSerializer(serializers.Serializer):
    """权限删除序列化器"""

    class Meta:
        model = Permission

    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

    def delete_permission(self):
        return self.Meta.model.objects.filter(pk__in=self.validated_data.get('pk_list')).delete()[0]


class MPermSerializer(serializers.Serializer):
    """管理员管理商家所属的角色的权限序列化器"""

    sid = serializers.IntegerField(required=False)  # 用户id，根据sid来找到对应的商家
    pid = serializers.ListField(child=serializers.CharField(max_length=8), allow_empty=False)  # 权限id集
    rid = serializers.IntegerField(required=False)  # 角色id

    class Meta:
        s_model = Seller
        p_model = Permission
        r_model = Role

    def validate_sid(self, value):
        """
        校验sid对应的商家是否存在
        如果存在获取其角色
        """
        try:
            return self.Meta.s_model.objects.get(pk=value)
        except self.Meta.s_model.DoesNotExist:
            raise DataNotExist()

    def validate_pid(self, value):
        """校验rid对应的权限集合是否存在"""
        return self.Meta.p_model.objects.filter(pk__in=value)

    def validate_rid(self, value):
        """校验rid对应的角色记录是否存在"""
        try:
            return self.Meta.r_model.objects.get(pk=value)
        except self.Meta.r_model.DoesNotExist:
            raise DataNotExist()

    def validate(self, attrs):
        data = {
            'permission': attrs.pop('pid')
        }
        data['role'] = attrs.pop('sid').role if attrs.get('sid', None) else attrs.pop('rid', None)
        if not data['role']:
            raise DataFormatError('缺少数据')
        return data

    def modify(self):
        """修改商家所属的角色的权限"""
        role = self.validated_data.pop('role')
        result = role.permission.set(self.validated_data.pop('permission'))  # 设置新的权限集

    def add(self):
        """增加商家所属的角色的权限"""
        role = self.validated_data.pop('role')
        role.permission.add(*self.validated_data.pop('permission'))

    def delete(self):
        """删除商家所属的角色的权限"""
        role = self.validated_data.pop('role')
        role.permission.remove(*self.validated_data.pop('permission'))
