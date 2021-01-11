# -*- coding: utf-8 -*-
# @Time  : 2021/1/1 下午2:12
# @Author : 司云中
# @File : urls.py
# @Software: Pycharm
from django.conf import settings
from django.urls import path, include

from analysis_app.apis.edge_api import record_browsing_login, record_browsing_every

app_name = 'analysis_app'

record_urlpatterns = [
    path('browser-users/', record_browsing_login),
    path('browser-whole/', record_browsing_every)
]

urlpatterns = [
    path(f'{settings.URL_PREFIX}/record', include(record_urlpatterns))
]
