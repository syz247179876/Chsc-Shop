# -*- coding: utf-8 -*-
# @Time  : 2020/9/18 上午9:04
# @Author : 司云中
# @File : voucher_manager.py
# @Software: Pycharm
import datetime

from django.db.models import Manager


class VoucherConsumerManager(Manager):
    """
    礼卷管理类
    默认生成具备默认QuerySet的Manager的实例
    """

    def _get_time(self):
        """计算当前时间"""
        return datetime.datetime.now()

    def acquire_coupon(self, user, validated_data):
        """
        获取优惠卷
        :param user: 用户instance
        :param validated_data: 验证后的数据OrderDict
        :return: the instance of model
        """

        time = self._get_time()
        coupon = self.create(user=user, acquire_time=time, **validated_data)
        return coupon

    def deduct_coupon(self, user, coupon_pk):
        """
        当用户兑换商品后 callback this function
        兑换完成
        扣除优惠卷
        :param user: 用户instance
        :param coupon_pk: 优惠卷pk
        :return: bool
        """

        return True if self.delete(pk=coupon_pk, user=user)[0] else False


    def get_all_voucher(self, user):
        """
        获取该用户下所有的优惠卷
        :param user: 用户对象
        :return: QuerySet
        """

        return self.filter(user=user)










