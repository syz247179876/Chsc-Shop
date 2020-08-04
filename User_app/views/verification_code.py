# -*- coding: utf-8 -*-
# @Time : 2020/5/5 14:20
# @Author : 司云中
# @File : verification_code.py
# @Software: PyCharm
from rest_framework.generics import GenericAPIView

from User_app.models.user_models import Consumer
from User_app.serializers.VerificationSerializerApi import VerificationSerializer
from User_app.views import tasks
from User_app.redis.user_redis import RedisVerificationOperation
from django.contrib.auth.models import User
from e_mall.loggings import Logging
from e_mall.response_code import response_code
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class SendCode:
    """decorator for sending code"""

    __slots__ = ('mode', 'time', 'response', 'redis')

    def __init__(self, mode, db):
        """mode choose from any function"""
        self.mode = mode  # 匹配方法
        self.redis = RedisVerificationOperation.choice_redis_db(db)
        self.time = 60 * 10
        self.response = None

    def __call__(self, func):
        def send(obj, way, number, **kwargs):
            """way choose from email and phone"""
            is_existed = func(obj, number)  # 根据number验证用户是否存在
            if is_existed:
                # 如果用户存在
                response_code_func = getattr(response_code, is_existed)
                return Response(response_code_func, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # 获取6位验证码
            code = tasks.set_verification_code()
            try:
                title = kwargs.pop('title')
                content = kwargs.pop('content') % {'code': code}
                if way == 'email':
                    # 异步队列发送验证码
                    tasks.send_email_verification.delay(title=title, content=content, user_email=number)
                    self.response = response_code.email_verification_success
                elif way == 'phone':
                    # tasks.send_email_verification.delay(title=title, content=content, user_email=number)
                    self.response = response_code.phone_verification_success
                # 保存验证码
                self.redis.save_code(number, code, self.time)
                return Response(self.response, status=status.HTTP_200_OK)
            except Exception as e:
                # fail to send
                consumer_logger.error('{}-send_email:{}'.format(self.mode, str(e)))
                return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return send


class VerificationBase(GenericAPIView):
    title = None
    content = None
    aim_user = None
    _redis = RedisVerificationOperation.choice_redis_db('redis')
    serializer_class = VerificationSerializer

    @staticmethod
    def get_key(key):
        """the key for verification code"""
        return key

    @SendCode('register', 'redis')
    def send_email_code(self, email):
        """send email verification code to register"""
        try:
            User.objects.get(email=email)
            # email was existed
            return 'user_existed'
        except User.DoesNotExist:
            return None

    @SendCode('register', 'redis')
    def send_phone_code(self, phone):
        """send phone verification code to register"""
        try:
            Consumer.consumer_.get(phone=phone)
            # email was existed
            return 'user_existed'
        except User.DoesNotExist:
            return None

    @SendCode('bind', 'redis')
    def send_email_code_bind(self, email):
        """send email verification code to bind"""
        try:
            User.objects.get(email=email)
            return None
        except User.DoesNotExist:
            return 'user_not_existed'

    @SendCode('bind', 'redis')
    def send_phone_code_bind(self, phone):
        """send phone verification code to bind"""
        try:
            Consumer.consumer_.get(phone=phone)
            return None
        except Consumer.DoesNotExist:
            return 'user_not_existed'

    @SendCode('setpay', 'redis')
    def send_phone_code_pay(self, phone):
        """send phone verification code to bind"""
        try:
            Consumer.consumer_.get(phone=phone)
            return None
        except Consumer.DoesNotExist:
            return 'user_not_existed'


class VerificationCodeRegister(VerificationBase):
    title = '吃货商城用户注册'
    content = '亲爱的用户,【吃货们的】商城欢迎您,您的邀请码%(code)s,有效期10分钟，如非本人操作，请勿理睬！'

    def factory(self, validated_data):
        """set factory to manage all functions in this class"""
        way = validated_data.get('way')
        func_list = {
            'email': 'send_email_code',
            'phone': 'send_phone_code',
        }
        func = func_list.pop(way)
        number = validated_data.get(way)  # email or phone or any other
        result = getattr(self, func)
        common_logger.info(number)
        return result(way, number, title=self.title, content=self.content)

    def post(self, request):
        """send verification code for user who is registering"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.factory(serializer.validated_data)


class VerificationCodeBind(VerificationBase):
    title = '吃货商城用户%(way)s绑定'
    content = '亲爱的【吃货商城】用户,您正在绑定手机或邮箱,您的换绑验证码为%(code)s,有效期10分钟，' \
              '如非本人操作，请勿理睬！'

    def factory(self, validated_data):
        """set factory to manage all functions in this class"""
        way = validated_data.get('way')
        func_list = {
            'email': 'send_email_code_bind',
            'phone': 'send_phone_code_bind',
        }
        func = func_list.pop(way)
        number = validated_data.get(way)  # email or phone or any other
        self.title = self.title % {'way': way}
        result = getattr(self, func)
        return result(way, number, title=self.title, content=self.content)

    def post(self, request):
        """send verification code to change bind"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.factory(serializer.validated_data)


class VerificationCodePay(VerificationBase):
    title = '吃货商城用户%(way)设置支付密码'
    content = '亲爱的【吃货商城】用户,您正在为您的账户设置密码,您的设置支付密码的短信验证码为%(code)s,' \
              '有效期10分钟，如非本人操作，请勿理睬！'

    def post(self, request):
        """send verification code to set password of pay"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        way = serializer.validated_data.get('way')
        phone = serializer.validated_data.get(way)
        return self.send_phone_code_pay(way, phone, title=self.title, content=self.content)


class VerificationCodeShopperRegister(VerificationBase):
    title = '吃货商城用户%(way)开店'
    content = '亲爱的【吃货商城】用户,您正在为您的账户设置密码,您的设置支付密码的短信验证码为%(code)s,' \
              '有效期10分钟，如非本人操作，请勿理财！'

    def post(self, request):
        """send verification code to register shopper"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        way = serializer.validated_data.get('way')
        email = serializer.validated_data.get(way)
        return self.send_email_code(way, email, title=self.title, content=self.content)
