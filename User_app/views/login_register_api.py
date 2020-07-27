# -*- coding: utf-8 -*-
# @Time : 2020/5/7 18:42
# @Author : 司云中
# @File : login_register_api.py
# @Software: PyCharm

from rest_framework_jwt.views import ObtainJSONWebToken

from User_app.models.user_models import Consumer
from User_app.redis.user_redis import RedisVerificationOperation
from django.contrib.auth.models import User
from e_mall.authentication_consumer import EmailOrUsername, Phone
from e_mall.loggings import Logging
from e_mall.response_code import response_code
from rest_framework.response import Response
from rest_framework.views import APIView

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class LoginAPIView(ObtainJSONWebToken):
    """ 使用JWT登录"""
    pass


class RegisterLoginAPIView(APIView):
    """用户注册"""
    redis = RedisVerificationOperation.choice_redis_db('redis')

    def register_phone(self, request, password, code):
        """手机注册"""
        phone = request.data.get('phone')
        try:
            # 判断手机号是否注册，若有，抛出异常
            Consumer.consumer_.get(phone=phone)
            return Response(response_code.user_existed)
        except Consumer.DoesNotExist:
            code_status = self.redis.check_code(phone, code)
            # 验证码错误或者过期
            if not code_status:
                return Response(response_code.verification_code_error)
        except Exception as e:
            consumer_logger.error('register_phone_error:{}'.format(e))
            return Response(response_code.server_error)

        # 验证码正确，手机号尚未使用
        try:
            consumer = User.objects.create_user(
                username='chch%s' % phone,
                password=password,
            )
            Consumer.consumer_.create(consumer=consumer, phone=phone)
            # 使用jwt登录，跳转到登录界面
        except Exception as e:
            consumer_logger.error('register_email_create_error:{}'.format(e))
            return Response(response_code.server_error)
        else:
            return Response(response_code.register_success)

    def register_email(self, request, password, code):
        """邮箱注册"""
        email = request.data.get('email')
        try:
            # 判断邮箱是否已注册，若有，抛出异常
            User.objects.get(email=email)
            return Response(response_code.user_existed)
        except User.DoesNotExist:
            code_status = self.redis.check_code(email, code)
            # 验证码错误或者过期
            if not code_status:
                return Response(response_code.verification_code_error)

        # 验证码正确，邮箱尚未使用
        try:
            user = User.objects.create_user(
                username='chch%s' % email,
                password=password,
                email=email,
            )
            Consumer.consumer_.create(user=user)
        except Exception as e:
            consumer_logger.error('register_email_create_error:{}'.format(e))
            return Response(response_code.server_error)
        else:
            return Response(response_code.register_success)

    def factory(self, request, password, verification_code, way):
        """简单工厂管理用户不同注册方式"""
        func_list = {
            'email': 'register_email',
            'phone': 'register_phone'
        }
        func = func_list.pop(way)
        result = getattr(self, func)
        return result(request, password, verification_code)

    def post(self, request):
        """用户注册POST请求"""
        password = request.data.get('password')
        verification_code = request.data.get('verification_code')
        way = request.data.get('way')
        return self.factory(request, password, verification_code, way)
