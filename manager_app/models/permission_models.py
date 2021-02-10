# -*- coding: utf-8 -*-
# @Time  : 2021/2/10 上午8:31
# @Author : 司云中
# @File : permission_models.py
# @Software: Pycharm

from django.db import models
from django.utils.translation import gettext_lazy as _



class ManagerPermission(models.Model):
    """
    管理员权限表
    """

    name = models.CharField(verbose_name=_('权限名'), max_length=30)

    code_name = models.CharField(verbose_name=_('权限代码'), max_length=6, unique=True)

    description = models.CharField(verbose_name=_('权限描述'), max_length=128)

    class Meta:
        db_table = 'manager_permission'

