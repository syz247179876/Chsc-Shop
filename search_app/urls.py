# -*- coding: utf-8 -*-
# @Time  : 2020/11/14 下午8:06
# @Author : 司云中
# @File : urls.py
# @Software: Pycharm
from django.urls import path
from django.conf import settings

from search_app.apis.heat_api import HeatSearchOperation
from search_app.apis.history_api import HistoryOperation
from search_app.apis.search_api import CommoditySearchOperation

app_name = 'search_app'

urlpatterns = [
    path(f'{settings.URL_PREFIX}/search/', CommoditySearchOperation.as_view(), name='search'),
    path(f'{settings.URL_PREFIX}/history/', HistoryOperation.as_view(), name='history_search'),
    path(f'{settings.URL_PREFIX}/heat/', HeatSearchOperation.as_view(), name='heat')
]
#
# router = DefaultRouter()
# router.register(r'search-chsc-api', CommoditySearchOperation, basename='search')
