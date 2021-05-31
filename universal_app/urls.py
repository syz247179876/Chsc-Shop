# -*- coding: utf-8 -*-
# @Time  : 2021/1/1 下午2:27
# @Author : 司云中
# @File : urls.py
# @Software: Pycharm
from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from universal_app.apis.common_api import SettingsApiView
from universal_app.apis.verification_code import VerificationCodeRegister, VerificationCodeShopperOpenStore, \
    VerificationCodeBind, VerificationCodeModifyPassword, VerificationCodeLogin

app_name = 'universal_app'

# 验证码子路由
code_urlpatterns = [
    path('login/', VerificationCodeLogin.as_view()),
    path('register/', VerificationCodeRegister.as_view()),
    path('store/', VerificationCodeShopperOpenStore.as_view()),
    path('bind/', VerificationCodeBind.as_view()),
    path('password/', VerificationCodeModifyPassword.as_view()),
]

urlpatterns = [
    path(f'{settings.URL_PREFIX}/verification-code/', include(code_urlpatterns)),
]


router = DefaultRouter()
router.register(f'{settings.URL_PREFIX}/settings', SettingsApiView, basename='settings')
urlpatterns += router.urls