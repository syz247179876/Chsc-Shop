# -*- coding: utf-8 -*-
# @Time  : 2021/2/18 下午5:26
# @Author : 司云中
# @File : permission.py
# @Software: Pycharm

import jwt
from django.conf import settings
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.permissions import BasePermission
from rest_framework_jwt.settings import api_settings

from Emall.exceptions import UserForbiddenError, AuthenticationError, UserNotExists
from manager_app.models import Managers
from django.utils.translation import gettext_lazy as _

from seller_app.models import Seller

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


def get_permission_token(request):
    """从请求头获取权限token"""
    token = request.META.get(settings.HEADERS_TOKEN_KEY.get('seller-permission'), b'')
    if not token:
        raise UserForbiddenError()
    if isinstance(token, str):
        token = token.encode(HTTP_HEADER_ENCODING)
    return token


def get_permission(request):
    """从权限token中解析该用户具备的权限"""
    token = get_permission_token(request)
    try:
        payload = jwt_decode_handler(token)
    except jwt.ExpiredSignature:
        msg = _('Signature has expired.')
        raise AuthenticationError(msg)
    except jwt.DecodeError:
        msg = _('Error decoding signature.')
        raise AuthenticationError(msg)
    except jwt.InvalidTokenError:
        msg = _('Incorrect authentication credentials')
        raise AuthenticationError(msg)

    mid = payload.get('mid', None)  # manager的id
    if not mid:
        raise UserForbiddenError()
    try:
        seller = Seller.objects.select_related('role').prefetch_related('role__permission').get(pk=mid)
        # 如果当前商家没有对应任何角色 或者  如果商家对应某个角色,但是该角色没有任何权限
        if not seller.role or not seller.role.permission:
            raise UserForbiddenError()
        allow_permission = seller.role.permission.all()  # 返回字段的值,只返回单个字段
        return allow_permission
    except Managers.DoesNotExist:
        raise UserNotExists()


def get_pid(request):
    """从请求头中获取权限pid"""

    return request.META.get(settings.HEADERS_TOKEN_KEY.get('backend-request-permission'), None)


class SellerPermissionValidation(BasePermission):
    """校验商家每个request请求的权限是否满足"""

    def has_permission(self, request, view):
        """
        从请求头部中获取pid,然后
        :param request: 请求
        :param view: 视图
        :return: bool
        """

        payload = request.jwt_payload
        sid = payload.get('sid', None)
        if not sid:
            raise UserForbiddenError('用户无请求权限')
        seller = Seller.objects.select_related('role').prefetch_related('role__permission').get(pk=sid)
        permissions = seller.role.permission.values_list('pid', flat=True)
        return self.judge_header_permission(request, permissions)

    def judge_header_permission(self, request, permissions):
        permission_number = get_pid(request)
        return permission_number in permissions
