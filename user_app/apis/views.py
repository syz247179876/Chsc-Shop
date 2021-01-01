# -*- coding: utf-8 -*-
# @Time : 2020/5/8 18:37
# @Author : 司云中
# @File : apis.py
# @Software: PyCharm

from django.shortcuts import render
from django.views.decorators.cache import cache_page
from Emall.loggings import Logging

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


@cache_page(60 * 60)
def login_page(request):
    return render(request, 'login.html')


@cache_page(60 * 60)
def register_page(request):
    return render(request, 'register.html')
