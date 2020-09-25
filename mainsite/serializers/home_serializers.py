# -*- coding: utf-8 -*- 
# @Time : 2020/6/1 17:19 
# @Author : 司云中 
# @File : home_serializers.py
# @Software: PyCharm
import math

from Shop_app.models.commodity_models import Commodity
from rest_framework import serializers


class GoodsSerializerApi(serializers.ModelSerializer):
    discount_price = serializers.SerializerMethodField()  # 商品打完折后的价格

    def get_discount_price(self, obj):
        """计算打折后的价格"""
        return obj.price * obj.discounts

    @staticmethod
    def get_limit_goods(**data):
        """获取限量的商品,后期改成推荐算法，利用贝叶斯分布"""
        if 'page' not in data:
            return None
        try:
            page = int(data.get('page')[0])
            limit = int(data.get('limit')[0]) if 'limit' in data else 8
            start = (page - 1) * limit
            end = page * limit
            all_instances = Commodity.commodity_.filter(status='1')  # 商品总价格
            counts = all_instances.count()  # 商品总数
            page = math.ceil(counts / limit)
            instances = all_instances.order_by('-image')[start:end]
            return instances, page
        except Commodity.DoesNotExist:
            return None

    class Meta:
        model = Commodity
        fields = ('pk', 'commodity_name', 'discount_price', 'intro', 'sell_counts', 'image', 'discounts_intro')
        read_only_fields = ('pk', 'commodity_name', 'discount_price', 'intro', 'sell_counts', 'image', 'discounts_intro')
