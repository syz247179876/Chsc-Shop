import json

from django.contrib.auth import get_user_model
from django.test import TestCase

# Create your tests here.

import os

from rest_framework.response import Response


def create_null_role_manager():
    """创建无角色的管理者"""
    user = User.objects.create_superuser(username='syz4', password='syzxss247179876')
    manager = Managers.manager_.create(user=user)
    return manager

def get_role_permission(pk):
    """获取管理者的角色和权限"""
    manager = Managers.manager_.select_related('role').prefetch_related('role__permission').get(pk=2)
    print(manager.role.permission.all())
    return manager.role.permission.all()

from rest_framework import serializers


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Emall.settings")
    import django
    django.setup()
    # manager = create_null_role_manager()

    from manager_app.models import Managers, ManagerPermission, ManagerRole


    class PermissionSerializer(serializers.ModelSerializer):
        class Meta:
            model = ManagerPermission
            fields = ['name']

    # 尝试获取没有角色的manager

    s = PermissionSerializer(instance=get_role_permission('2'), many=True)
    print(Response(s.data))

