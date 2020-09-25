# -*- coding: utf-8 -*- 
# @Time : 2020/6/1 10:19 
# @Author : 司云中 
# @File : payment_api.py 
# @Software: PyCharm
import os
import time

from django.core.files.storage import FileSystemStorage
from rest_framework.generics import GenericAPIView

from Order_app.models.order_models import Order_basic
from Payment_app.serializers.payment_serializers import PaymentSerializer
from alipay import AliPay

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from e_mall import settings
from e_mall.loggings import Logging
from e_mall.response_code import response_code
from rest_framework.response import Response
from rest_framework.views import APIView

common_logger = Logging.logger('django')

order_logger = Logging.logger('order_')


class PaymentOperation(GenericAPIView):
    """
    the operation of Ali payment
    """

    serializer_class = PaymentSerializer

    app_private_key_string = open(settings.APP_KEY_PRIVATE_PATH).read()
    alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()

    @property
    def get_alipay(self):
        # 创建alipay对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=settings.ALIPAY_NOTIFY_URL,  # 处理支付宝回调的POST请求
            app_private_key_string=self.app_private_key_string,
            alipay_public_key_string=self.alipay_public_key_string,
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG,
        )
        return alipay

    @staticmethod
    def combine_str(alipay, order):
        """assemble the url of get"""
        # 组合url，用于返回给前端请求
        order_string = alipay.api_alipay_trade_page_pay(
            subject=settings.ALIPAY_SUBJECT,
            out_trade_no=order.orderId,  # 交易编号
            total_amount=str(order.total_price),  # 支付总金额，类型为Decimal(),不支持序列化，需要强转成str
            return_url=settings.ALIPAY_RETURN_URL,  # 支付成功后的回调地址,显示给用户
        )
        return order_string

    @method_decorator(login_required(login_url='consumer/login/'))
    def get(self, request):
        """
        创建订单基本信息,address,order_id
        核对总价钱
        """
        user = request.user

        # 不在这里创建
        order = self.get_serializer_class.create_order(request, user)
        if order is None:
            return Response(response_code.create_order_error)
        # 创建alipay对象
        alipay = self.get_alipay
        # 调用方法,生成url
        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        # 字符串拼接
        order_string = self.combine_str(alipay, order)
        # 4.返回url
        response_code.create_order_success.update({"alipay_url": settings.ALIPAY_GATE + order_string})
        return Response(response_code.create_order_success)

    def post(self, request):
        """this function used to accept the post returned by alipay"""
        # 验证是否支付成功
        data = request.data
        common_logger.info(data)
        sign = data.get('sign', None)
        alipay = self.get_alipay
        status = alipay.verify(data, sign)  # 验证签名
        if status:
            # modify order
            common_logger.info(data.get('out_trade_no'))
            return Response('2')
        else:
            return Response('3')


class UpdateOperation(APIView):

    @property
    def generate_trade_num(self):
        """生成交易号成功号"""
        return int(round(time.time() * 1000000))

    @staticmethod
    def update_order(order_id):
        """更新订单"""
        Order_basic.order_basic_.update(orderId=order_id)

    def get(self, request):
        # 用于回调用户界面，一般不做数据操作，不安全
        data = request.GET
        common_logger.info(data)
        out_trade_no = data.get('out_trade_no')
        total_amount = data.get('total_amount')

        # 更新交易状态及交易号
        Order_basic.order_basic_.filter(orderId=out_trade_no).update(status="2", trade_number=self.generate_trade_num)
        return redirect('/order/personal_order/')
