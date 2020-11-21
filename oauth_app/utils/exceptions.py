# -*- coding: utf-8 -*-
# @Time  : 2020/11/21 上午9:05
# @Author : 司云中
# @File : exceptions.py
# @Software: Pycharm

from rest_framework.exceptions import APIException
class QQServiceUnavailable(APIException):
    """对接QQ登录服务异常"""
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'

