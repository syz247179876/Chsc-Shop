# -*- coding: utf-8 -*-
# @Time  : 2020/9/18 上午10:57
# @Author : 司云中
# @File : urls.py
# @Software: Pycharm
from django.urls import path

from Voucher_app.views.bonus_api import VoucherOperation

app_name = 'Voucher_app'

urlpatterns = [
    path('voucher-chsc-api/', VoucherOperation.as_view(), name='voucher-chsc-api'),
]