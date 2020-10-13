# -*- coding: utf-8 -*-
# @Time  : 2020/10/13 下午9:35
# @Author : 司云中
# @File : verification_code.py
# @Software: Pycharm
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from CommonModule_app.serailizers.verification_serializers import VerificationSerializer, RetrieveCodeSerializer
from CommonModule_app.tasks import set_verification_code, send_email, send_phone
from Shopper_app.models.shopper_models import Shoppers
from User_app.models.user_models import Consumer
from e_mall.base_redis import BaseRedis
from e_mall.loggings import Logging
from e_mall.response_code import response_code
from e_mall.settings import TEMPLATES_CODE_RETRIEVE_PASSWORD

common_logger = Logging.logger('django')


class SendCode:
    """
    发送验证码类装饰器
    增强发送过程
    """

    __slots__ = ('mode', 'time', 'response', 'redis', 'results')

    def __init__(self, db):
        """初始化信息"""
        self.redis = BaseRedis.choice_redis_db(db)
        self.time = 60 * 10
        self.response = None

    def __call__(self, func):
        mode = func.__name__

        def send(obj, way, number, **kwargs):
            """选择手机号还是邮箱进行验证码发送"""
            is_existed = func(obj, number)  # 根据number验证用户是否存在,obj为类实例
            if is_existed:
                # 如果用户存在
                response_code_func = getattr(response_code, is_existed)
                return Response(response_code_func, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # 获取6位验证码
            code = set_verification_code()
            try:
                title = kwargs.pop('title')
                content = kwargs.pop('content') % {'code': code}
                if way == 'email':
                    # 异步任务队列发送验证码
                    send_email.delay(title=title, content=content, user_email=number)
                    self.response = response_code.email_verification_success
                elif way == 'phone':
                    # 发送手机验证码
                    template_code = kwargs.pop('template_code')
                    send_phone.delay(phone_numbers=number, template_code=template_code,
                                     template_param={'code': code})
                    self.response = response_code.phone_verification_success
                # 保存验证码
                self.redis.save_code(number, code, self.time)
                return Response(self.response, status=status.HTTP_200_OK)
            except Exception as e:
                # fail to send
                common_logger.info('{}-send_email:{}'.format(mode, str(e)))
                return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return send


class VerificationBase(GenericAPIView):
    title = None
    content = None
    aim_user = None
    _redis = BaseRedis.choice_redis_db('redis')
    serializer_class = VerificationSerializer

    @SendCode('redis')
    def user_email_register(self, email):
        """发送邮箱验证码用于 用户 or 商家 注册"""
        try:
            User.objects.get(email=email)
            return 'user_existed'
        except User.DoesNotExist:
            return None

    @SendCode('redis')
    def consumer_phone_register(self, phone):
        """发送手机号验证码用于用户注册"""
        try:
            Consumer.consumer_.get(phone=phone)
            return 'user_existed'
        except Consumer.DoesNotExist:
            return None

    @SendCode('redis')
    def shopper_phone_register(self, phone):
        """发送手机验证码用于商家注册"""
        try:
            Shoppers.shopper_.get(phone=phone)
            return None
        except Shoppers.DoesNotExist:
            return True

    @SendCode('redis')
    def user_phone_login(self, phone):
        """发送手机验证码用于用户登录"""
        try:
            Consumer.consumer_.get(phone=phone)
            return None
        except Consumer.DoesNotExist:
            return True

    @SendCode('redis')
    def shopper_phone_login(self, phone):
        """发送手机验证码用于商家登录"""
        try:
            Shoppers.shopper_.get(phone=phone)
            return None
        except Shoppers.DoesNotExist:
            return True

    @SendCode('redis')
    def user_email_bind(self, email):
        """发送邮箱验证码用于 用于 or 商家 绑定邮箱"""
        try:
            User.objects.get(email=email)
            return None
        except User.DoesNotExist:
            return True

    @SendCode('redis')
    def consumer_phone_bind(self, phone):
        """发送手机验证码用于用户绑定手机"""
        try:
            Consumer.consumer_.get(phone=phone)
            return None
        except Consumer.DoesNotExist:
            return True

    @SendCode('redis')
    def consumer_secret_pay(self, phone):
        """发送手机验证码用于用户秘保"""
        try:
            Consumer.consumer_.get(phone=phone)
            return None
        except Consumer.DoesNotExist:
            return True

    @SendCode('redis')
    def consumer_phone_modify_pwd(self, phone):
        """发送手机验证码用于用户修改密码"""
        try:
            Consumer.consumer_.get(phone=phone)
            return None
        except Consumer.DoesNotExist:
            return True

    @SendCode('redis')
    def consumer_email_modify_pwd(self, email):
        """发送邮箱验证码用于用户修改密码"""
        try:
            User.objects.get(email=email)
            return None
        except User.DoesNotExist:
            return True

    @SendCode('redis')
    def user_email_retrieve_pwd(self, email):
        """发送邮箱验证码用于用户/商家找回密码"""
        try:
            User.objects.get(email=email)
            return None
        except User.DoesNotExist:
            return True

    @SendCode('redis')
    def user_phone_retrieve_pwd(self, phone):
        """发送手机验证码用于用户/商家找回密码"""
        try:
            Consumer.consumer_.get(phone=phone)
            return None
        except Consumer.DoesNotExist:
            return True


class VerificationCodeRetrieve(VerificationBase):
    title = '吃货商城用户%(way)s找回密码'
    content = '亲爱的【吃货商城】用户,您正在找回密码,您的验证码为%(code)s,有效期10分钟，' \
              '如非本人操作，请勿理睬！'

    serializer_class = RetrieveCodeSerializer

    def factory(self, validated_data):
        """set factory to manage all functions in this class"""
        way = validated_data.get('way')
        func_list = {
            'email': 'user_email_retrieve_pwd',
            'phone': 'user_phone_retrieve_pwd',
        }
        func = func_list.pop(way)
        number = validated_data.get(way)  # email or phone or any other
        self.title = self.title % {'way': way}
        result = getattr(self, func)
        return result(way, number, title=self.title, content=self.content,
                      template_code=TEMPLATES_CODE_RETRIEVE_PASSWORD)

    def post(self, request):
        """发送验证码(忘记密码）"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.factory(serializer.validated_data)
