# -*- coding: utf-8 -*-
# @Time  : 2021/2/10 下午12:19
# @Author : 司云中
# @File : models.py
# @Software: Pycharm
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class ManagerPermission(models.Model):
    """
    管理员权限表
    """

    name = models.CharField(verbose_name=_('权限名'), max_length=30)

    pid = models.CharField(verbose_name=_('权限代码'), max_length=8, unique=True)

    description = models.CharField(verbose_name=_('权限描述'), max_length=128)

    manager_permission_ = Manager()

    class Meta:
        db_table = 'manager_permission'


class RoleManager(models.Manager):
    """
    角色管理
    """


class ManagerRole(models.Model):
    """
    角色模型
    """

    role_name = models.CharField(verbose_name=_('角色名'), max_length=15)

    description = models.CharField(verbose_name=_('角色描述'),max_length=128)

    permission = models.ManyToManyField(to=ManagerPermission, related_name='role')

    rid = models.CharField(verbose_name=_('角色代码'), max_length=8, unique=True)

    role_ = RoleManager()

    class Meta:
        db_table = 'manager_role'


class Managers(models.Model):
    """管理者表"""

    # 用户名
    user = models.OneToOneField(
        User,
        verbose_name=_('管理者'),
        on_delete=models.CASCADE,
        related_name='manager',
    )
    role = models.ForeignKey(to=ManagerRole, on_delete=models.SET_NULL, related_name='manager', null=True)

    manager_ = Manager()

    class Meta:
        db_table = 'managers'