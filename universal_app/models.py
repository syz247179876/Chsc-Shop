from django.db import models

from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

class Permission(models.Model):
    """
    管理员权限表
    """

    name = models.CharField(verbose_name=_('权限名'), max_length=30)

    pid = models.CharField(verbose_name=_('权限代码'), max_length=8, unique=True)

    description = models.CharField(verbose_name=_('权限描述'), max_length=128)

    objects = Manager()

    class Meta:
        db_table = 'permission'


class Role(models.Model):
    """
    角色模型
    """

    role_name = models.CharField(verbose_name=_('角色名'), max_length=15, unique=True)

    description = models.CharField(verbose_name=_('角色描述'),max_length=128)

    permission = models.ManyToManyField(to=Permission, related_name='role')

    rid = models.CharField(verbose_name=_('角色代码'), max_length=8, unique=True)

    objects = Manager()

    class Meta:
        db_table = 'role'