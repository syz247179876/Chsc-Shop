# -*- coding: utf-8 -*-
# @Time  : 2020/9/13 上午12:11
# @Author : 司云中
# @File : voucher_serializers.py
# @Software: Pycharm
import datetime

from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from shop_app.models.commodity_models import Commodity
from voucher_app.models.voucher_models import Voucher, VoucherConsumer


class CommoditySerializer(serializers.ModelSerializer):
    """与优惠卷有关的商品序列化器"""

    class Meta:
        model = Commodity
        fields = ('commodity_name',)


class VoucherInfoSerializer(serializers.ModelSerializer):
    """优惠卷信息序列化器"""

    commodity = CommoditySerializer(read_only=True)

    class Meta:
        model = Voucher
        fields = ('bonus_title', 'store', 'commodity', 'is_efficient', 'price', 'start_date', 'end_date')


class VoucherConsumerSerializer(serializers.ModelSerializer):
    """用户优惠卷序列化器"""
    pk = serializers.IntegerField(min_value=1, write_only=True)

    voucher = VoucherInfoSerializer(read_only=True)

    def validate(self, attrs):
        """过滤pk，并创建voucher实例，替换原来的pk"""
        queryset = Voucher.voucher_.filter(is_grant=True, counts__gt=0, end_date__gt=datetime.datetime.now())
        filter_kwargs = {'pk':attrs.get('pk')}
        obj = get_object_or_404(queryset, **filter_kwargs)  # 控制只有允许queryset，redis_manager，model对象作为第一argument传入
        attrs.update({'pk',obj})
        return attrs


    class Meta:
        model = VoucherConsumer
        fields = ('pk', 'voucher')
