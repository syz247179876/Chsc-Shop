# -*- coding: utf-8 -*-
# @Time  : 2020/8/20 下午1:56
# @Author : 司云中
# @File : signals.py
# @Software: Pycharm
from django.dispatch import Signal

add_favorites = Signal(providing_args=["instance", "user", "queryset"])

delete_favorites = Signal(providing_args=["user", "collection_pk", "is_all"])