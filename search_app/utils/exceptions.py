# -*- coding: utf-8 -*-
# @Time  : 2021/4/12 下午2:48
# @Author : 司云中
# @File : exceptions.py
# @Software: Pycharm
from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class ESConnectionError(APIException):
    """ES服务器连接异常"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('ES服务器连接异常')
    default_code = 'ES Server Connection Error'


class ESConflict(APIException):
    """ES服务器关键字冲突"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('ES关键字冲突')
    default_code = 'ES Keyword Conflict'


class ESNotFound(APIException):
    """ES找不到关键信息"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('ES找不到关键信息')
    default_code = 'ES Data Not Found'


class ESRequest(APIException):
    """ES数据解析错误"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('ES数据解析错误')
    default_code = 'ES Data Parse Error'