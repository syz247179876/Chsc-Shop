# -*- coding: utf-8 -*-
# @Time  : 2020/11/20 下午11:57
# @Author : 司云中
# @File : qq_api.py
# @Software: Pycharm
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from Emall.base_api import check_code
from Emall.response_code import response_code
from oauth_app.models import OauthQQ
from oauth_app.serializers.oauth_serializer import generate_token, QQOauthSerializer, jwt_response_payload_handler
from oauth_app.utils.exceptions import QQServiceUnavailable
from oauth_app.utils.qq_utils import OAuthQQ
from user_app.redis.user_redis import RedisUserOperation
from django.db import transaction, DataError, DatabaseError

User = get_user_model()


class QQOauthUrl(GenericAPIView):
    """
    QQ登录操作类之获取提供用于登录的QQ
    """

    def get(self, request):
        next = request.query_params.get('next')
        oauth = OAuthQQ(state=next)
        login_url = oauth.generate_qq_login_url()
        return Response({'login_url': login_url})


def generate_response(user, next):
    """生成jwt响应体"""
    response_data = generate_token(user, next=next)  # 获取jwt token, 字典格式
    response_data.update({'next': next})
    response = Response(response_data)

    if api_settings.JWT_AUTH_COOKIE:
        expiration = (datetime.utcnow() +
                      api_settings.JWT_EXPIRATION_DELTA)
        # 对应配置中的Token名称
        response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                            response_data.get('token'),
                            expires=expiration,
                            httponly=True)
    return response  # 登录成功,自动跳转页面


class QQOauthAccessToken(GenericAPIView):
    """
    携带code和state回调该视图
    请求qq服务器获取access token
    """
    @property
    def next_validator(self):
        """校验next的url格式"""
        error_messages = {
            'invalid': '请输入一个有效url地址'
        }
        return URLValidator(message=error_messages['invalid'])

    def get(self, request):
        code = request.query_params.get('code')
        next = request.query_params.get('next')
        if not code or not next:
            raise ValidationError({'message':'缺少code或next'})
        try:
            oauth = OAuthQQ(state=next)
            access_token = oauth.get_access_token(code)  # 获取access_token
            open_id = oauth.get_openid(access_token)  # 获取唯一身份
        except QQServiceUnavailable as e:
            return Response({'message':'QQ服务器异常,稍后重试'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            qq_user = OauthQQ.qq_manager.existed_user(open_id)
            if qq_user:
                generate_response(qq_user.user, oauth.state)
            else:
                # 用户不存在,返回access_token,不立即重定向, 让用户注册绑定QQ
                response_data = jwt_response_payload_handler(access_token=access_token, next=next, redirect=False)
                return Response(response_data)


class BindQQAPIView(GenericAPIView):
    """绑定QQ第三方登录"""

    serializer_class = QQOauthSerializer

    redis = RedisUserOperation.choice_redis_db('redis')

    def retrieve_openid(self, validated_data):
        """拿前端传过来的access_token再去请求open_id"""
        try:
            oauth = OAuthQQ(state=next)
            open_id = oauth.get_openid(validated_data.get('access_token'))
            return open_id, oauth.state
        except QQServiceUnavailable:
            return Response({'QQ服务器异常,请稍后重试'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def post(self, request):
        """手机绑定"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        check_code(self.redis, serializer.validated_data)  # 校验验证码
        open_id, next = self.retrieve_openid(serializer.validated_data)  # 获取openid和next的url

        # 创建用户
        try:
            with transaction.atomic():  # 开启事务
                user = User.objects.create_consumer(
                    password=serializer.validated_data.get('password'),
                    phone=serializer.validated_data.get('phone'),
                )
                qq_user = OauthQQ.qq_manager.create_qq_user(user, open_id)
                if not qq_user:
                    return Response(response_code.bind_qq, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError:
            return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return generate_response(user, next)
