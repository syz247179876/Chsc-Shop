# -*- coding: utf-8 -*-
# @Time : 2020/5/7 18:42
# @Author : 司云中
# @File : login_register_api.py
# @Software: PyCharm


from datetime import datetime
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_jwt.settings import api_settings
from user_app.models import Consumer
from user_app.redis.user_redis import RedisUserOperation
from user_app.serializers.login_serializers import UserJwtLoginSerializer
from user_app.serializers.register_serializers import RegisterSerializer
from Emall.loggings import Logging
from Emall.response_code import response_code
from rest_framework.response import Response
from django.db import transaction, DatabaseError
from rest_framework.generics import GenericAPIView

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')

jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class LoginAPIView(GenericAPIView):
    """ 使用JWT登录"""

    serializer_class = UserJwtLoginSerializer

    redis = RedisUserOperation.choice_redis_db('redis')

    def get_serializer_context(self):
        """添加redis到额外环境中"""
        context = super().get_serializer_context()
        context.update({'redis': self.redis})
        return context

    @staticmethod
    def remember_username(response, is_remember, login_id):
        """设置cookie，本地暂存用户名1周"""
        if is_remember:
            response.set_cookie('login_id', login_id, max_age=7 * 24 * 3600)
        else:
            response.delete_cookie('login_id', login_id)

    def post(self, request, *args, **kwargs):
        """用户登录"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.object.get('user') or request.user
        token = serializer.object.get('token')
        is_remember = serializer.object.get('is_remember')
        previous_page = serializer.object.get('previous_page')
        # 加密，如果配置中支持刷新，则更新token,将user调用中间件赋给request.user
        response_data = jwt_response_payload_handler(token, user, request)
        response_data.update({'previous_page': previous_page})
        response = Response(response_data)
        self.remember_username(response, is_remember, user.get_username())  # 设置cookie，记住用户名
        # 将token存到response的cookie中，设置有效的日期
        if api_settings.JWT_AUTH_COOKIE:
            expiration = (datetime.utcnow() +
                          api_settings.JWT_EXPIRATION_DELTA)
            # 对应配置中的Token名称
            response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                token,
                                expires=expiration,
                                httponly=True)
        return response


class RegisterAPIView(GenericAPIView):
    """用户注册"""
    redis = RedisUserOperation.choice_redis_db('redis')

    serializer_class = RegisterSerializer

    User = get_user_model()

    def register_phone(self, validated_data):
        """手机注册"""
        phone = validated_data.get('phone')
        try:
            # 判断手机号是否注册，若有，抛出异常
            self.User.objects.get(phone=phone)
            return Response(response_code.user_existed)
        except self.User.DoesNotExist:
            code_status = self.redis.check_code(phone, validated_data.get('code'))
            # 验证码错误或者过期
            if not code_status:
                return Response(response_code.verification_code_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            consumer_logger.error('register_phone_error:{}'.format(e))
            return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 验证码正确，手机号尚未使用
        try:
            with transaction.atomic():  # 开启事务
                user = self.User.objects.create_consumer(
                    username=phone,
                    phone=phone,
                )
                Consumer.consumer_.create(user=user)
            # 使用jwt登录，跳转到登录界面
        except DatabaseError as e:
            consumer_logger.error('register_email_create_error:{}'.format(e))
            return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(response_code.register_success, status=status.HTTP_200_OK)

    def register_email(self, validated_data):
        """邮箱注册"""
        email = validated_data.get('email')
        username = validated_data.get('username')
        try:
            # 判断邮箱是否已注册，若有，抛出异常
            self.User.objects.get(email=email)
            return Response(response_code.user_existed, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except self.User.DoesNotExist:
            code_status = self.redis.check_code(email, validated_data.get('code'))
            # 验证码错误或者过期
            if not code_status:
                return Response(response_code.verification_code_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 验证码正确，邮箱尚未使用
        try:
            with transaction.atomic():  # 开启事务
                user = self.User.objects.create_consumer(
                    username=username,
                    password=validated_data.get('password'),
                    email=email,
                )
                Consumer.consumer_.create(user=user)
        except DatabaseError as e:
            consumer_logger.error('register_email_create_error:{}'.format(e))
            return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(response_code.register_success, status=status.HTTP_200_OK)

    def factory(self, validated_data):
        """简单工厂管理用户不同注册方式"""
        func_list = {
            'email': 'register_email',
            'phone': 'register_phone'
        }
        func = func_list.get(validated_data.get('way'))
        result = getattr(self, func)
        return result(validated_data)

    def post(self, request):
        """用户注册"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.factory(serializer.validated_data)
