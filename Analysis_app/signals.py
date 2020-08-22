# -*- coding: utf-8 -*-
# @Time  : 2020/8/21 下午11:17
# @Author : 司云中
# @File : signals.py
# @Software: Pycharm

from django.core.signals import Signal

login_user_browser_times = Signal(providing_args=["instance", "date"])   # 每天登录的用户浏览总数统计

user_login_mouth = Signal(providing_args=["instance", "date"])       # 某个用户每个月登录的总次数

user_browser_times = Signal(providing_args=["ip", "date"])                 # 每天所有用户的浏览次数