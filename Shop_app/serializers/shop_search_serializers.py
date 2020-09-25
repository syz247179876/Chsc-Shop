# -*- coding: utf-8 -*-
# @Time  : 2020/8/11 下午9:38
# @Author : 司云中
# @File : shop_search_serializers.py
# @Software: Pycharm
from rest_framework import serializers

from Shop_app.models.commodity_models import Commodity


class CommoditySerializer(serializers.ModelSerializer):
    """商品序列化器"""

    class Meta:
        model = Commodity
        fields = '__all__'


# class ShopSearchSerializer(HaystackSerializer):
#     """搭配ES序列化器"""
#
#     # object = CommoditySerializer(read_only=True)
#
#     class Meta:
#         index_classes = [CommodityIndex]  # 索引类名
#         fields = ('text', 'commodity_name', 'shopper')  # 第一个参数为索引类中的字段，第二个参数为序列化器返回
