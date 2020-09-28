# -*- coding: utf-8 -*-
# @Time  : 2020/8/21 下午11:17
# @Author : 司云中
# @File : signals.py
# @Software: Pycharm

from django.core.signals import Signal

login_user_browser_times = Signal(providing_args=["instance"])   # 每天登录的用户浏览总数统计

user_browser_times = Signal(providing_args=["ip"])                 # 每天所有用户的浏览次数


buy_category = Signal(providing_args=["category"])                       # 购买商品记录，商品种类记录+1


user_recommend = Signal(providing_args=["category", "instance"])         # 用户推荐记录+1