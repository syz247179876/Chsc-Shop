# -*- coding: utf-8 -*-
# @Time  : 2021/2/5 下午5:04
# @Author : 司云中
# @File : authentication.py
# @Software: Pycharm
import jwt
from django.contrib.auth import get_user_model
from django.utils.encoding import smart_text
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_decode_handler

from Emall.exceptions import AuthenticationError


def jwt_get_user_id_from_payload_handler(payload):
    """
    从payload中获取user_id
    """

    return payload.get('user_id', None)


class MyJsonWebTokenAuthentication(BaseAuthentication):
    """
    重写JWT认证类
    1.用于有效获取Token
    2.校验Token
    3.生成User对象
    """
    User = get_user_model()

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise returns `None`.
        """
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None
        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise AuthenticationError(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise AuthenticationError(msg)
        except jwt.InvalidTokenError:
            msg = _('Incorrect authentication credentials')
            raise AuthenticationError(msg)

        user = self.authenticate_credentials(payload)
        setattr(request, 'jwt_payload', payload)  # 方便校验permission使用
        return (user, jwt_value)

    def get_jwt_value(self, request):
        """
        获取jwt值

        1.先从headers中取出 `HTTP_AUTHORIZATION`字段,如果有进入第三步,没有进入第二步
        2.从cookie中获取 `Bearer-Token`字段值, 如果有,返回token,没有返回None
        3.对从headers中取出的数据进行切片,总共两部分,第一部分与服务器指定的头部进行匹配,如果匹配成功,返回第二部分Token值,否则返回None

        """
        auth = get_authorization_header(request).split()
        auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

        # 如果头部没有目标字段,则从cookie中拿取token
        if not auth:
            if api_settings.JWT_AUTH_COOKIE:
                return request.COOKIES.get(api_settings.JWT_AUTH_COOKIE)
            return None

        if smart_text(auth[0].lower()) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise AuthenticationError(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise AuthenticationError(msg)

        return auth[1]

    def authenticate_credentials(self, payload):
        """
        从payload中获取user id
        :param payload: 有效载荷
        :return: user obj
        """
        user_id = jwt_get_user_id_from_payload_handler(payload)
        if not user_id:
            msg = _('Invalid payload.')
            raise AuthenticationError(msg)

        try:
            user = self.User.objects.get(pk=user_id)
        except self.User.DoesNotExist:
            msg = _('Invalid signature.')
            raise AuthenticationError(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise AuthenticationError(msg)

        return user
