# -*- coding: utf-8 -*-
# @Time  : 2021/1/1 下午2:27
# @Author : 司云中
# @File : urls.py
# @Software: Pycharm
from django.conf import settings
from django.urls import path, include

from universal_app.apis.verification_code import VerificationCodeRegister, VerificationCodeShopperOpenStore, \
    VerificationCodeBind, VerificationCodeModifyPassword

app_name = 'universal_app'

# 验证码子路由
code_urlpatterns = [
    path('register/', VerificationCodeRegister.as_view()),
    path('store/', VerificationCodeShopperOpenStore.as_view()),
    path('bind/', VerificationCodeBind.as_view()),
    path('password', VerificationCodeModifyPassword.as_view()),
]

urlpatterns = [
    path(f'{settings.URL_PREFIX}/verification-code/', include(code_urlpatterns)),
]
