# -*- coding: utf-8 -*-
# @Time : 2020/5/7 18:42
# @Author : 司云中
# @File : login_register_api.py
# @Software: PyCharm
from rest_framework import status
from rest_framework_jwt.views import ObtainJSONWebToken

from User_app.models.user_models import Consumer
from User_app.redis.user_redis import RedisUserOperation
from django.contrib.auth.models import User

from User_app.serializers.RegisterSerializerApi import RegisterSerializer

from e_mall.loggings import Logging
from e_mall.response_code import response_code
from rest_framework.response import Response
from django.db import transaction, DatabaseError
from rest_framework.generics import GenericAPIView

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class LoginAPIView(ObtainJSONWebToken):
    """ 使用JWT登录"""
    pass


class RegisterAPIView(GenericAPIView):
    """用户注册"""
    redis = RedisUserOperation.choice_redis_db('redis')

    serializer_class = RegisterSerializer

    def register_phone(self, validated_data):
        """手机注册"""
        phone = validated_data.get('phone')
        try:
            # 判断手机号是否注册，若有，抛出异常
            Consumer.consumer_.get(phone=phone)
            return Response(response_code.user_existed)
        except Consumer.DoesNotExist:
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
                user = User.objects.create_user(
                    username='chch%s' % phone,
                    password=validated_data.get('password'),
                )
                Consumer.consumer_.create(user=user, phone=phone)
            # 使用jwt登录，跳转到登录界面
        except DatabaseError as e:
            consumer_logger.error('register_email_create_error:{}'.format(e))
            return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(response_code.register_success, status=status.HTTP_200_OK)

    def register_email(self, validated_data):
        """邮箱注册"""
        email = validated_data.get('email')
        try:
            # 判断邮箱是否已注册，若有，抛出异常
            User.objects.get(email=email)
            return Response(response_code.user_existed, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except User.DoesNotExist:
            code_status = self.redis.check_code(email, validated_data.get('code'))
            # 验证码错误或者过期
            if not code_status:
                return Response(response_code.verification_code_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 验证码正确，邮箱尚未使用
        try:
            with transaction.atomic():  # 开启事务
                user = User.objects.create_user(
                    username='chch%s' % email,
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
