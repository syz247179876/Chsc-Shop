# -*- coding: utf-8 -*-
# @Time  : 2020/11/14 下午7:51
# @Author : 司云中
# @File : signals.py
# @Software: Pycharm

from django.dispatch import Signal

record_search = Signal(providing_args=["request", "key"])

del_search_single = Signal(providing_args=["request", "key"])

del_search_all = Signal(providing_args=["request"])