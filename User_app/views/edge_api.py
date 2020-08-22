# -*- coding: utf-8 -*-
# @Time  : 2020/8/22 下午8:16
# @Author : 司云中
# @File : edge_api.py
# @Software: Pycharm
import datetime

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from e_mall.loggings import Logging

common_logger = Logging.logger('django')

from Analysis_app.signals import login_user_browser_times, user_browser_times


@api_view()
@permission_classes([IsAuthenticated])  # 必须登录
def record_browsing_login(request):
    """
    用户进入首页浏览，记录登录用户活跃量
    :param request: Request对象
    :return: 
    """
    user = request.user
    result = login_user_browser_times.send(
        sender=User,
        instance=user,
        date=datetime.date.today()
    )
    common_logger.info(result)
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view()
def record_browsing_every(request):
    """
    记录一天内所有身份用户的浏览次数
    :param request: Request对象
    :return:
    """

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # 这里是真实的ip
    else:
        ip = request.META.get('REMOTE_ADDR')  # 这里获得代理ip,如果没有代理也是真实IP
    common_logger.info(ip)
    result = user_browser_times.send(
        sender=None,
        ip=ip,
        date=datetime.date.today()
    )
    common_logger.info(result)

    return Response(status=status.HTTP_204_NO_CONTENT)

