# -*- coding: utf-8 -*-
# @Time  : 2021/4/13 下午2:30
# @Author : 司云中
# @File : diplay_serializers.py
# @Software: Pycharm


from rest_framework import serializers

from seller_app.models import Store
from shop_app.models.commodity_models import Commodity, Sku, SkuProps, SkuValues, Freight, FreightItem


class CommodityCardSerializer(serializers.ModelSerializer):
    """商品卡片显示序列化器"""

    class Meta:
        model = Commodity
        fields = ('pk', 'commodity_name', 'price', 'favourable_price', 'details', 'intro', 'little_image')


class CommodityFreightItemSerializer(serializers.ModelSerializer):
    """商品运费模板项序列化器"""

    class Meta:
        model = FreightItem
        fields = '__all__'


class CommodityFreightSerializer(serializers.ModelSerializer):
    """商品运费模板序列化器"""

    freight_items = CommodityFreightItemSerializer(many=True)

    class Meta:
        model = Freight
        fields = '__all__'


class CommodityStoreSerializer(serializers.ModelSerializer):
    """指定商品所属的店铺的信息序列化器"""

    class Meta:
        model = Store
        fields = '__all__'


class CommoditySkuValuesSerializer(serializers.ModelSerializer):
    """指定商品的sku的属性值序列化器"""

    # 商品默认可以选中,为False就是不可选中,表示多个类目属性组成sku无效
    status = serializers.BooleanField(default=True)

    # 商品是否可以被选中,默认没被选中
    is_choice = serializers.BooleanField(default=False)

    class Meta:
        model = SkuValues
        fields = '__all__'


class CommoditySkuPropsSerializer(serializers.ModelSerializer):
    """指定商品的sku的属性序列化器"""

    sku_values = CommoditySkuValuesSerializer(many=True)

    class Meta:
        model = SkuProps
        fields = '__all__'


class CommodityDetailSerializer(serializers.ModelSerializer):
    """商品详情页信息序列化器"""

    sku_props = CommoditySkuPropsSerializer(many=True)
    store = CommodityStoreSerializer()
    freight = CommodityFreightSerializer()

    class Meta:
        model = Commodity
        fields = '__all__'
