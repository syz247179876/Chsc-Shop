# -*- coding: utf-8 -*-
# @Time  : 2021/2/10 下午12:59
# @Author : 司云中
# @File : urls.py
# @Software: Pycharm
from django.conf import settings
from django.urls import path, include

from manager_app.apis.auth_api import ManagerRoleApiView, ManagerLoginApiView, ManagerRegisterApiView

app_name = "manager_app"

auth_patterns = [
    path('login/', ManagerLoginApiView.as_view()),
    path('register/', ManagerRegisterApiView.as_view()),
    path('role/', ManagerRoleApiView.as_view()),
]

urlpatterns = {
    path(f'{settings.URL_PREFIX}/manager/auth', include(auth_patterns))
}
