# -*- coding: utf-8 -*-
# @Time  : 2020/9/2 下午9:24
# @Author : 司云中
# @File : common.py
# @Software: Pycharm
from payment_app.models.Alipay_models import PayInformation
from voucher_app.models.voucher_models import Integrals
from voucher_app.signals import increase_integral, decrease_integral


class IntegralUtilOperation:

    def __init__(self):
        self.connect()

    def trans_money(self, money):
        """
        将money等价转为积分
        规则：
        1.总价低于15的订单，默认2积分
        2.总价高于15的订单，除15 + 2,例如300块商品，转换的积分为104
        """
        return int(money**0.7 + 50)


    def connect(self):
        """注册积分模块信号"""
        increase_integral.connect(self._increase_integral, sender=PayInformation)
        decrease_integral.connect(self._decrease_integral, sender=Integrals)


    def _increase_integral(self, sender, total_price, user, **kwargs):
        """
        购买商品，按照商品价格等价转换为积分
        :param sender: 基本订单模型类
        :param instance: 订单模型实例
        :param user:  购买商品的用户
        :param kwargs: 额外参数
        :return: 积分值
        """
        integral = self.trans_money(total_price)
        user.integral += integral
        user.save(update_fields=['integral'])
        return integral



    def _decrease_integral(self, sender, integral_commodity_pk, user, **kwargs):
        """
        当用户在积分商城中兑换了商品后，减少积分
        :param sender:积分商品模型类
        :param integral_commodity_pk: 选择兑换的商品pk
        :param user:当前兑换积分的用户
        :param kwargs:额外参数
        :return: bool  （是否兑换成功）
        """
        try:
            integral_commodity = sender.integral_commodity_.get(pk=integral_commodity_pk)
            integral = integral_commodity.integral_price
            user.integral -= integral
            user.save(update_fields=['integral'])
            return True
        except sender.DoesNotExist:
            return False











integral_operation = IntegralUtilOperation()

