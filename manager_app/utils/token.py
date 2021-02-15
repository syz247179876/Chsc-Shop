# -*- coding: utf-8 -*-
# @Time  : 2021/2/9 下午11:52
# @Author : 司云中
# @File : token.py
# @Software: Pycharm
from calendar import timegm
from datetime import datetime

from rest_framework_jwt.settings import api_settings


def generate_payload(user):
    """
    为不同权限的管理者生成不同的token
    追加role角色,稍后请求根据role获取用户具备的权限
    """
    payload = {
        'mid':user.manager.pk,
        'username':user.is_super_manager,
        'role':user.manager.role,
        'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA,
    }

    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.utcnow().utctimetuple()
        )

    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.JWT_AUDIENCE

    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER

    return payload


