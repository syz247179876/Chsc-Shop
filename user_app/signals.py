# -*- coding: utf-8 -*-
# @Time  : 2020/8/20 下午1:56
# @Author : 司云中
# @File : signals.py
# @Software: Pycharm
from django.dispatch import Signal

add_favorites = Signal(providing_args=["instance", "user", "queryset"])

delete_favorites = Signal(providing_args=["user", "collection_pk", "is_all"])

# 获取存储用户收藏商品的{类型:次数}的zset
retrieve_collect = Signal()

# 获取存储用户浏览商品足迹的{类型:次数}的zset
retrieve_foot = Signal()

# 存储存储用户购买的商品的{类型:次数}的zset
retrieve_bought = Signal()

# 当用户收藏商品是，发送信号，记录商品类型和次数
collect_add_type = Signal(providing_args=["commodity_type"])

# 当用户浏览商品时，发送信号，记录商品类型和次数
foot_add_type = Signal(providing_args=["commodity_type"])

# 当用户购买完毕商品后，发送信号，记录商品类型和次数
bought_add_type = Signal(providing_args=["commodity_type"])