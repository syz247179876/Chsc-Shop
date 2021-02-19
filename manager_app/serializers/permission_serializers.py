# -*- coding: utf-8 -*-
# @Time  : 2021/2/15 下午2:40
# @Author : 司云中
# @File : permission_serializers.py
# @Software: Pycharm
import time

from rest_framework import serializers

from universal_app.models import Permission


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = ('pk', 'name', 'description', 'pid')
        read_only_fields = ('pk', )

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

    class Meta:
        model = Permission

    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

    def delete_permission(self):
        return self.Meta.model.objects.filter(pk__in=self.validated_data.get('pk_list')).delete()[0]
