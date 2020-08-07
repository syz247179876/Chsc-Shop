# -*- coding: utf-8 -*-
# @Time  : 2020/8/7 下午2:33
# @Author : 司云中
# @File : verification_code.py
# @Software: Pycharm
from User_app.views.verification_code import VerificationBase


class VerificationCodeShopperRegister(VerificationBase):
    title = '吃货商城用户%(way)开店'
    content = '亲爱的【吃货商城】用户,您正在开通您的店铺,您的店铺开通的短信验证码为%(code)s,' \
              '有效期10分钟，如非本人操作，请勿理财！'

    def post(self, request):
        """发送验证码（商家注册）"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        way = serializer.validated_data.get('way')
        phone = serializer.validated_data.get(way)
        return self.send_phone_code_shopper(way, phone, title=self.title, content=self.content)