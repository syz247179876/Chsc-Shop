# -*- coding: utf-8 -*-
# @Time  : 2021/2/10 上午9:03
# @Author : 司云中
# @File : role_models.py
# @Software: Pycharm

from django.db import models
from django.utils.translation import gettext_lazy as _

from manager_app.models.permission_models import ManagerPermission


class RoleManager(models.Manager):
    """
    角色管理
    """


class ManagerRole(models.Model):
    """
    角色模型
    """

    role_name = models.CharField(verbose_name=_('角色名'), max_length=15)

    description = models.CharField(verbose_name=_('角色描述'),max_length=20)

    permission = models.ManyToManyField(to=ManagerPermission, related_name='role')

    role_ = RoleManager()

    class Meta:
        db_table = 'manager_role'


