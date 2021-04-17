# -*- coding: utf-8 -*-
# @Time  : 2021/4/13 下午2:30
# @Author : 司云中
# @File : diplay_serializers.py
# @Software: Pycharm


from rest_framework import serializers
from shop_app.models.commodity_models import Commodity
class  CommodityCardSerializer(serializers.ModelSerializer):
    """商品卡片显示序列化器"""

    class Meta:
        model = Commodity
        fields = ('pk', 'commodity_name', 'price', 'favourable_price', 'details', 'intro', 'little_image')


class CommodityDetailSerializer(serializers.ModelSerializer):
    """商品详情页信息"""

    class Meta:
        model = Commodity
        fields = '__all__'