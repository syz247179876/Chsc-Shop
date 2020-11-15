# -*- coding: utf-8 -*-
# @Time  : 2020/11/14 下午8:06
# @Author : 司云中
# @File : urls.py
# @Software: Pycharm
from django.urls import path
from rest_framework.routers import DefaultRouter

from search_app.views.search_api import CommoditySearchOperation

app_name = 'search_app'

urlpatterns = [
    path('search-chsc-api/', CommoditySearchOperation.as_view(), name='search-chsc-search'),
]
#
# router = DefaultRouter()
# router.register(r'search-chsc-api', CommoditySearchOperation, basename='search')
