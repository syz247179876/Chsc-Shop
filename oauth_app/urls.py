# -*- coding: utf-8 -*-
# @Time  : 2020/11/21 下午2:23
# @Author : 司云中
# @File : urls.py
# @Software: Pycharm
from django.urls import path, include

from oauth_app.apis.qq_api import QQOauthUrl, QQOauthAccessToken, BindQQAPIView

app_name = 'oauth_app'

qq_urlpatterns = [
    path('entrance', QQOauthUrl.as_view(), name='qq-login-url-api'),
    path('token/', QQOauthAccessToken.as_view(), name='qq-login-access-token-api'),
    path('qq-login-bind-api/', BindQQAPIView.as_view(), name='qq-login-bind-api')
]

urlpatterns = [
    path('qq', include(qq_urlpatterns)),
]
