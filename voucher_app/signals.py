# -*- coding: utf-8 -*-
# @Time  : 2020/9/2 下午9:04
# @Author : 司云中
# @File : signals.py
# @Software: Pycharm


from django.dispatch import Signal


increase_integral = Signal(providing_args=["total_price, user"])  # 购买商品增加积分

decrease_integral = Signal(providing_args=["integral_commodity_pk, user"])  # 兑换商品时减少积分