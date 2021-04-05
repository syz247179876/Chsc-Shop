# -*- coding: utf-8 -*-
# @Time  : 2021/2/15 下午8:28
# @Author : 司云中
# @File : role_serializers.py
# @Software: Pycharm
from django.db import transaction, DatabaseError
from rest_framework import serializers

from Emall.exceptions import DataFormatError, DataNotExist
from seller_app.models import Seller
from universal_app.models import Role


class RoleSerializer(serializers.ModelSerializer):
    """管理员管理所有角色序列化器"""

    pid_list = serializers.ListField(child=serializers.CharField(max_length=8), allow_empty=True, write_only=True)

    class Meta:
        model = Role
        fields = ('pk', 'role_name', 'description', 'pid_list', 'rid')
        read_only_fields = ('pk',)

    def add_role(self):
        """添加角色信息"""
        credential = self.get_credential
        pid_list = self.validated_data.pop('pid_list')
        try:
            with transaction.atomic():
                role = self.Meta.model.objects.create(**credential)
                role.permission.add(*pid_list)
        except DatabaseError:
            raise DataFormatError('数据非法')

    def modify_role(self):
        """修改角色信息"""
        credential = self.get_credential
        pk = self.context.get('request').data.pop('pk')
        permission_list = self.validated_data.pop('pid_list')
        try:
            with transaction.atomic():
                role = self.Meta.model.objects.get(pk=pk)

                # TODO: 存在问题
                role.set(permission_list)
        except self.Meta.model.DoesNotExist:
            raise DataFormatError('数据不存在')
        except DatabaseError:
            raise DataFormatError('数据非法')

    @property
    def get_credential(self):
        return {
            'role_name': self.validated_data.pop('role_name'),
            'description': self.validated_data.pop('description'),
            'rid': self.validated_data.pop('rid')
        }


class RoleDeleteSerializer(serializers.Serializer):
    """权限管理中删除权限"""
    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


class MRoleSerializer(serializers.Serializer):
    """管理员管理商家所属的角色"""

    sid = serializers.IntegerField(required=False)  # 用户id
    rid = serializers.CharField(max_length=8)  # 角色id
    is_all = serializers.BooleanField(required=False)

    class Meta:
        s_model = Seller
        r_model = Role

    def validate_sid(self, value):
        """校验sid对应的商家是否存在"""
        try:
            return self.Meta.s_model.objects.get(pk=value)
        except self.Meta.s_model.DoesNotExist:
            raise DataNotExist()

    def validate_rid(self, value):
        """校验rid对应的角色是否存在"""
        try:
            return self.Meta.r_model.objects.get(pk=value)
        except self.Meta.r_model.DoesNotExist:
            raise DataNotExist()

    def validate(self, attrs):
        data = {
            'role':attrs.pop('rid')
        }
        # 如果is_all存在，修改全部商家角色，添加如data
        # 如果is_all为False且sid不存在，则抛出缺少数据异常
        # 其余情况，is_all为False，存在seller，添加如data
        # 返回
        if attrs.get('is_all', False):
            data['is_all'] = attrs.pop('is_all')
        elif not attrs.get('sid', None):
            raise DataFormatError('缺少数据')
        else:
            data['seller'] = attrs.pop('sid')
            data['is_all'] = False
        return data

    def modify(self):
        """修改某个用户的角色"""
        if self.validated_data.pop('is_all'):
            return self.modify_all()
        else:
            return self.modify_aim()

    def modify_all(self):
        """修改所有商家的角色"""
        return self.Meta.s_model.objects.all().update(role=self.validated_data.pop('role'))

    def modify_aim(self):
        """修改指定商家的角色"""
        seller = self.validated_data.pop('seller')
        seller.role = self.validated_data.pop('role')
        seller.save()
        return 1

