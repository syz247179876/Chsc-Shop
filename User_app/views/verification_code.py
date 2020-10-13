# -*- coding: utf-8 -*-
# @Time : 2020/5/5 14:20
# @Author : 司云中
# @File : verification_code.py
# @Software: PyCharm
from CommonModule_app.verification_code import VerificationBase
from e_mall.loggings import Logging
from e_mall.settings import TEMPLATES_CODE_REGISTER, TEMPLATES_CODE_MODIFY_PASSWORD

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')



class VerificationCodeRegister(VerificationBase):
    title = '吃货商城用户注册'
    content = '亲爱的用户,【吃货们的】商城欢迎您,您的邀请码%(code)s,有效期10分钟，如非本人操作，请勿理睬！'

    def factory(self, validated_data):
        """set factory to manage all functions in this class"""
        way = validated_data.get('way')
        func_list = {
            'email': 'user_email_register',
            'phone': 'consumer_phone_register',
        }
        func = func_list.pop(way)
        number = validated_data.get(way)  # phone
        result = getattr(self, func)
        return result(way, number, title=self.title, content=self.content, template_code=TEMPLATES_CODE_REGISTER)

    def post(self, request):
        """
        send verification code for user who is registering
        发送验证码（用户注册）
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.factory(serializer.validated_data)


class VerificationCodeBind(VerificationBase):
    title = '吃货商城用户%(way)s绑定'
    content = '亲爱的【吃货商城】用户,您正在绑定邮箱,您的换绑验证码为%(code)s,有效期10分钟，' \
              '如非本人操作，请勿理睬！'

    def factory(self, validated_data):
        """set factory to manage all functions in this class"""
        way = validated_data.get('way')
        func_list = {
            'email': 'user_email_bind',
            'phone': 'consumer_phone_bind',
        }
        func = func_list.pop(way)
        number = validated_data.get(way)  # email or phone or any other
        self.title = self.title % {'way': way}
        result = getattr(self, func)
        return result(way, number, title=self.title, content=self.content, template_code=TEMPLATES_CODE_REGISTER)

    def post(self, request):
        """发送验证码（改绑/绑定）"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.factory(serializer.validated_data)


class VerificationCodePay(VerificationBase):
    title = '吃货商城用户%(way)设置支付密码'
    content = '亲爱的【吃货商城】用户,您正在为您的账户设置密码,您的设置支付密码的短信验证码为%(code)s,' \
              '有效期10分钟，如非本人操作，请勿理睬！'

    def post(self, request):
        """发送验证码（支付）"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        way = serializer.validated_data.get('way')
        phone = serializer.validated_data.get(way)
        return self.consumer_secret_pay(way, phone, title=self.title, content=self.content)


class VerificationCodeShopperRegister(VerificationBase):
    title = '吃货商城用户%(way)开店'
    content = '亲爱的【吃货商城】用户,您正在开通您的店铺,您的店铺开通的短信验证码为%(code)s,' \
              '有效期10分钟，如非本人操作，请勿理睬！'

    def post(self, request):
        """发送验证码（商家注册）"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        way = serializer.validated_data.get('way')
        phone = serializer.validated_data.get(way)
        return self.shopper_phone_register(way, phone, title=self.title, content=self.content,
                                           template_code=TEMPLATES_CODE_REGISTER)


class VerificationCodeShopperLogin(VerificationBase):
    title = '吃货商城用户%(way)'
    content = '亲爱的【吃货商城】用户,您正在登录店铺,您的短信验证码为%(code)s,' \
              '有效期10分钟，如非本人操作，请勿理睬！'

    def post(self, request):
        """发送验证码（商家注册）"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        way = serializer.validated_data.get('way')
        phone = serializer.validated_data.get(way)
        return self.shopper_phone_login(way, phone, title=self.title, content=self.content,
                                        template_code=TEMPLATES_CODE_REGISTER)


class VerificationCodeModifyPassword(VerificationBase):
    """手机验证"""
    title = '吃货商城用户%(way)密码修改提醒'
    content = '亲爱的【吃货商城】用户,您正在为您的账户修改密码,您的修改密码的短信验证码为%(code)s,' \
              '有效期10分钟，如非本人操作，请勿理睬！'

    def post(self, request):
        """发送验证码（修改密码）"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        way = serializer.validated_data.get('way')
        phone = serializer.validated_data.get(way)
        return self.consumer_phone_modify_pwd(way, phone, title=self.title, content=self.content,
                                              template_code=TEMPLATES_CODE_MODIFY_PASSWORD)
