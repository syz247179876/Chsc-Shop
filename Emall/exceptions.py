# -*- coding: utf-8 -*-
# @Time  : 2021/1/1 下午7:46
# @Author : 司云中
# @File : exceptions.py
# @Software: Pycharm
from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class NoBindPhone(APIException):
    """尚未绑定手机号异常"""
    status_code = status.HTTP_204_NO_CONTENT
    default_detail = _('用户尚未绑定手机号')
    default_code = 'No Bind Phone'


class UserNotExists(APIException):
    """用户不存在异常"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('用户不存在')
    default_code = 'User Not Exists'


class UserExists(APIException):
    """用户存在异常"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('用户已存在')
    default_code = 'User has existed'


class UserTimesLimit(APIException):
    """用户限流"""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = _('请求超过限制')
    default_code = 'Request exceed limit'


class ThirdServiceBase(APIException):
    """第三方服务异常基类"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('服务异常')
    default_code = 'Service Support Error'


class QQServiceError(APIException):
    """QQ第三方服务异常"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('QQ服务提供存在异常')
    default_code = 'QQ Service Error'


class WeiBoServiceError(APIException):
    """微博第三方服务异常"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('微博第三方服务存在异常')
    default_code = 'WeiBo Service Error'


class CodeError(APIException):
    """sms服务异常"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('短信验证码提供异常')
    default_code = 'SMS Error'
