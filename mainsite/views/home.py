# -*- coding: utf-8 -*-
# @Time : 2020/5/8 18:37
# @Author : 司云中
# @File : home.py
# @Software: PyCharm
from User_app.models.user_models import Address
from django.shortcuts import render

# Create your views here.

from django.views.decorators.cache import cache_page
from e_mall.loggings import Logging

common_logger = Logging.logger('django')


def home_page(request):
    """主页"""
    user = getattr(request, 'user', None)
    if user.is_authenticated:
        try:
            default_address = Address.address_.get(user=user, default_address=True)
        except Address.DoesNotExist:
            default_address = None
    else:
        default_address = None
    data = {
        'default_address': default_address
    }
    return render(request, 'home.html', data)
