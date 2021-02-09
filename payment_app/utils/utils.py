# -*- coding: utf-8 -*-
# @Time  : 2020/9/11 上午9:58
# @Author : 司云中
# @File : common.py
# @Software: Pycharm
from datetime import datetime

from order_app.models.order_models import Order_basic
from payment_app.models.Alipay_models import PayInformation
from payment_app.signals import save_payment
from voucher_app.signals import increase_integral


class PaymentUtilOperation:

    model = PayInformation

    def __init__(self):
        self.connect()

    def connect(self):
         """注册支付模块信号"""
         save_payment.connect(self._create_payment, sender=Order_basic)


    def _create_payment(self, sender, instance, trade_id,**kwargs):
        """
        1.创建支付记录
        2.回调积分信号函数
        :param sender:订单基本模型类
        :param instance:Order_basic实例
        :param trade_id:交易号
        :param kwargs:额外参数
        :return: bool（是否支付成功) integral(积分值）
        """
        sender.payment_.create(order_basic=instance, trade_id=trade_id, generate_time=datetime.now())

        integral = increase_integral.send(
            sender=PayInformation,
            total_price=instance.total_price,
            trade_id=trade_id
        )
        return True, integral[0][1]




