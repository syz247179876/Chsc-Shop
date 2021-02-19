# -*- coding: utf-8 -*-
# @Time  : 2021/2/10 下午12:19
# @Author : 司云中
# @File : models.py
# @Software: Pycharm
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from universal_app.models import Role

User = get_user_model()


class Managers(models.Model):
    """管理者表"""

    # 用户名
    user = models.OneToOneField(
        User,
        verbose_name=_('管理者'),
        on_delete=models.CASCADE,
        related_name='manager',
    )
    role = models.ForeignKey(to=Role, on_delete=models.SET_NULL, related_name='manager', null=True)

    objects = Manager()

    class Meta:
        db_table = 'managers'