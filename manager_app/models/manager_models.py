# -*- coding: utf-8 -*-
# @Time  : 2021/2/10 上午9:24
# @Author : 司云中
# @File : manager_models.py
# @Software: Pycharm
from django.db import models

from manager_app.models.role_models import ManagerRole
from user_app.models import AbstractUser


class Manager(AbstractUser):

    role_id = models.OneToOneField(to=ManagerRole, on_delete=False)

    class Meta:
        db_table = 'manager'