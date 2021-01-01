# -*- coding: utf-8 -*-
# @Time  : 2020/9/18 上午10:57
# @Author : 司云中
# @File : urls.py
# @Software: Pycharm
from django.urls import path

from voucher_app.apis.bonus_api import VoucherOperation
from django.conf import settings

app_name = 'Voucher_app'

urlpatterns = [
    path(f'{settings.URL_PREFIX}/voucher', VoucherOperation.as_view(), name='voucher-chsc-api'),
]