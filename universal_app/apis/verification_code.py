# -*- coding: utf-8 -*-
# @Time : 2020/5/5 14:20
# @Author : 司云中
# @File : verification_code.py
# @Software: PyCharm

"""兼容不使用第三方服务短信模板的情况"""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from Emall.base_redis import BaseRedis
from Emall.loggings import Logging
from Emall.response_code import response_code
from Emall.settings import TEMPLATES_CODE_REGISTER
from Emall.settings import TEMPLATES_CODE_RETRIEVE_PASSWORD, TEMPLATES_CODE_REGISTER, TEMPLATES_CODE_LOGIN, \
    TEMPLATES_CODE_IDENTIFY, TEMPLATES_CODE_MODIFY_PASSWORD
from universal_app.tasks import set_verification_code, send_email, send_phone
from user_app.serializers.verification_serializers import VerificationSerializer, RetrieveCodeSerializer, \
    PhoneOnlySerializer

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class SendCode:
    """
    发送验证码类装饰器
    增强发送过程
    """

    __slots__ = ('mode', 'time', 'response', 'redis', 'results')

    def __init__(self, db):
        """
        初始化信息
        :param db:setting中配置的缓存键名
        """

        self.redis = BaseRedis.choice_redis_db(db)
        self.time = 60 * 10
        self.response = None

    def __call__(self, func):
        mode = func.__name__

        def send(obj, way, number, **kwargs):
            """选择手机号还是邮箱进行验证码发送"""
            is_satisfied = func(obj, number)  # 根据number验证用户是否存在,obj为类实例
            if is_satisfied:
                # 如果用户存在
                response_code_func = getattr(response_code, is_satisfied)
                return Response(response_code_func)
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
    """
    验证码基类
    """
    title = None  # 短信 or 邮件标题
    content = None  # 短信 or 邮件内容
    aim_user = None  # 目标用户
    serializer_class = VerificationSerializer

    User = get_user_model()  # 获取User模型

    FUNC_LIST_NONE = {
        'email': 'user_email_none',
        'phone': 'user_phone_none',
    }

    FUNC_LIST_EXIST = {
        'email': 'user_email_exist',
        'phone': 'user_phone_exist',
    }

    @SendCode('redis')
    def user_email_none(self, email):
        """发送邮箱验证码用于 用户 or 商家 注册"""
        try:
            self.User.objects.get(email=email)
            return 'user_existed'
        except self.User.DoesNotExist:
            return None

    @SendCode('redis')
    def user_phone_none(self, phone):
        """发送手机号验证码用于用户 or 商家 注册"""
        try:
            self.User.objects.get(phone=phone)
            return 'user_existed'
        except self.User.DoesNotExist:
            return None

    @SendCode('redis')
    def user_phone_exist(self, phone):
        """发送手机验证码用于商家注册"""
        try:
            self.User.objects.get(phone=phone)
            return None
        except self.User.DoesNotExist:
            return 'user_not_existed'

    @SendCode('redis')
    def user_email_exist(self, email):
        """
        基于存在的用户向其邮箱中发送验证码
        """
        try:
            self.User.objects.get(email=email)
            return None
        except self.User.DoesNotExist:
            return 'user_not_existed'


class FactoryBase(VerificationBase):
    """执行工厂基类"""

    def factory(self, validated_data, func_list, template_code):
        """
        执行工厂
        :param validated_data:验证后的数据
        :param func_list:函数列表
        :return:
        """
        way = validated_data.get('way')
        func = func_list.get(way)
        number = validated_data.get(way)  # email or phone or any other
        result = getattr(self, func)
        return result(way, number, title=self.title, content=self.content,
                      template_code=template_code)


class VerificationCodeRetrieve(FactoryBase):
    """找回密码"""
    title = '吃货商城用户%(way)s找回密码'
    content = '亲爱的【吃货商城】用户,您正在找回密码,您的验证码为%(code)s,有效期10分钟，' \
              '如非本人操作，请勿理睬！'
    serializer_class = RetrieveCodeSerializer

    def post(self, request):
        """发送验证码(忘记密码）"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.factory(serializer.validated_data, func_list=self.FUNC_LIST_EXIST, template_code=None)


class VerificationCodeLogin(FactoryBase):
    """用户登录"""

    title = "吃或商城用户登录"
    content = '亲爱的用户,【吃货们的】商城欢迎您,您的邀请码%(code)s,有效期10分钟，如非本人操作，请勿理睬！'

    def post(self, request):
        """发送验证码(登录)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.factory(serializer.validated_data, func_list=self.FUNC_LIST_EXIST,
                            template_code=TEMPLATES_CODE_LOGIN)


class VerificationCodeRegister(FactoryBase):
    """用户注册"""
    title = '吃货商城用户注册'
    content = '亲爱的用户,【吃货们的】商城欢迎您,您的邀请码%(code)s,有效期10分钟，如非本人操作，请勿理睬！'

    def post(self, request):
        """发送验证码（改绑/绑定）"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.factory(serializer.validated_data, func_list=self.FUNC_LIST_NONE,
                            template_code=TEMPLATES_CODE_REGISTER)


class VerificationCodeBind(FactoryBase):
    """绑定邮箱 or 手机号"""
    title = '吃货商城用户绑定'
    content = '亲爱的【吃货商城】用户,您正在绑定帐号,您的换绑验证码为%(code)s,有效期10分钟，' \
              '如非本人操作，请勿理睬！'

    def post(self, request):
        """发送验证码（改绑/绑定）"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.factory(serializer.validated_data, func_list=self.FUNC_LIST_EXIST,
                            template_code=TEMPLATES_CODE_REGISTER)


# class VerificationCodePay(VerificationBase):
#     title = '吃货商城用户%(way)设置支付密码'
#     content = '亲爱的【吃货商城】用户,您正在为您的账户设置密码,您的设置支付密码的短信验证码为%(code)s,' \
#               '有效期10分钟，如非本人操作，请勿理睬！'
#
#     def post(self, request):
#         """发送验证码（支付）"""
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         way = serializer.validated_data.get('way')
#         phone = serializer.validated_data.get(way)
#         return self.consumer_secret_pay(way, phone, title=self.title, content=self.content)


class VerificationCodeShopperOpenStore(VerificationBase):
    title = '吃货商城用户开店'
    content = '亲爱的【吃货商城】用户,您正在开通您的店铺,您的店铺开通的短信验证码为%(code)s,' \
              '有效期10分钟，如非本人操作，请勿理睬！'

    serializer_class = PhoneOnlySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        way = serializer.validated_data.get('way')
        phone = serializer.validated_data.get(way)
        return self.user_phone_exist(way, phone, title=self.title, content=self.content,
                                     template_code=TEMPLATES_CODE_REGISTER)


class VerificationCodeModifyPassword(FactoryBase):
    """手机验证"""
    title = '吃货商城用户密码修改提醒'
    content = '亲爱的【吃货商城】用户,您正在为您的账户修改密码,您的修改密码的短信验证码为%(code)s,' \
              '有效期10分钟，如非本人操作，请勿理睬！'

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.factory(serializer.validated_data, func_list=self.FUNC_LIST_EXIST,
                            template_code=TEMPLATES_CODE_REGISTER)
