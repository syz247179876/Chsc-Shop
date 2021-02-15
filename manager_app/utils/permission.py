# -*- coding: utf-8 -*-
# @Time  : 2021/2/15 上午11:53
# @Author : 司云中
# @File : permission.py
# @Software: Pycharm
import jwt

from Emall.exceptions import UserForbiddenError, AuthenticationError, UserNotExists
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework_jwt.settings import api_settings

from manager_app.models import Managers

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
def get_permission_token(request):
    """从请求头获取权限token"""
    token = request.Meta.get('ROLE_PERMISSION',b'')
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

    mid = payload.get('mid') # manager的id
    try:
        manager = Managers.manager_.select_related('role').prefetch_related('role__permission').get(pk=mid)
        # 如果当前管理者没有对应任何角色 或者  如果管理者对应某个角色,但是该角色没有任何权限
        if not manager.role or not manager.role.permission:
            raise UserForbiddenError()
        allow_permission = manager.role.permission.all()  # 返回字段的值,只返回单个字段
        return allow_permission
    except Managers.DoesNotExist:
        raise UserNotExists()

