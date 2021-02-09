# -*- coding: utf-8 -*-
# @Time : 2020/5/7 18:42
# @Author : 司云中
# @File : auth_api.py
# @Software: PyCharm


from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from Emall.exceptions import UserExists, CodeError, UniversalServerError
from Emall.loggings import Logging
from Emall.response_code import response_code
from oauth_app.serializers.oauth_serializer import jwt_response_payload_handler
from user_app.models import Consumer
from user_app.redis.user_redis import RedisUserOperation
from user_app.serializers.login_serializers import UserJwtLoginSerializer
from user_app.serializers.register_serializers import RegisterSerializer

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')

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
    def remember_username(response, is_remember, login_name):
        """设置cookie，本地暂存用户名1周"""
        if is_remember:
            response.set_cookie('login_name', '22222', max_age=7 * 24 * 3600)
        else:
            response.delete_cookie('login_name', '222222')

    @staticmethod
    def save_cookie(response, response_obj):
        """校验jwt"""
        if api_settings.JWT_AUTH_COOKIE:
            expiration = (datetime.utcnow() +
                          api_settings.JWT_EXPIRATION_DELTA)
            # 对应配置中的Token名称
            response_obj.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    response.get('token'),
                                    expires=expiration,
                                    httponly=True)

    def post(self, request, *args, **kwargs):
        """用户登录"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = serializer.object
        # 加密，如果配置中支持刷新，则更新token,将user调用中间件赋给request.user
        response.pop('user')
        response_obj = Response(response)
        # self.remember_username(response_obj, response.get('is_remember'),
        #                        response.pop('user').get_username())  # 设置cookie，记住用户名
        # # 将token存到response的cookie中，设置有效的日期
        self.save_cookie(response, response_obj)
        return response_obj


class RegisterAPIView(GenericAPIView):
    """用户注册"""
    redis = RedisUserOperation.choice_redis_db('redis')

    serializer_class = RegisterSerializer

    User = get_user_model()

    def register_phone(self, validated_data):
        """手机注册"""
        phone = validated_data.get('phone')
        try:
            # 判断手机号是否注册，若没有，校验手机号
            self.User.objects.get(phone=phone)
            raise UserExists()
        except self.User.DoesNotExist:
            code_status = self.redis.check_code(phone, validated_data.get('code'))
            # 验证码错误或者过期
            if not code_status:
                raise CodeError()
        except Exception as e:
            consumer_logger.error('register_phone_error:{}'.format(e))
            raise UniversalServerError()

        # 验证码正确，手机号尚未使用
        try:
            current_day = datetime.today()
            with transaction.atomic():
                user = self.User.objects.create_consumer(
                    password=validated_data.get('password'),
                    username=f"用户:{phone}",
                    phone=phone,
                    last_login=current_day
                )
                Consumer.consumer_.create(
                    user=user
                )
            # 使用jwt登录，跳转到登录界面
        except Exception as e:
            consumer_logger.error('register_email_create_error:{}'.format(e))
            raise UniversalServerError()
        else:
            return Response(response_code.register_success)

    def register_email(self, validated_data):
        """邮箱注册"""
        email = validated_data.get('email')
        username = validated_data.get('username')
        try:
            # 判断邮箱是否已注册，若没有，校验手机号
            self.User.objects.get(email=email)
            raise UserExists()
        except self.User.DoesNotExist:
            code_status = self.redis.check_code(email, validated_data.get('code'))
            # 验证码错误或者过期
            if not code_status:
                raise CodeError()

        # 验证码正确，邮箱尚未使用
        try:
            current_day = datetime.today()
            with transaction.atomic():
                user = self.User.objects.create_consumer(
                    password=validated_data.get('password'),
                    username=username,
                    email=email,
                    last_login=current_day
                )
                Consumer.consumer_.create(
                    user=user
                )
        except Exception as e:
            consumer_logger.error('register_email_create_error:{}'.format(e))
            return UniversalServerError()
        return Response(response_code.register_success)

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
