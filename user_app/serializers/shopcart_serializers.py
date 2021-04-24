# -*- coding: utf-8 -*-
# @Time : 2020/5/30 10:38
# @Author : 司云中
# @File : shopcart_serializers.py
# @Software: PyCharm

from rest_framework import serializers

from Emall.exceptions import DataNotExist
from Emall.loggings import Logging
from seller_app.models import Store
from shop_app.models.commodity_models import Commodity, Sku
from user_app.model.trolley_models import Trolley

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class ShopCartStoreSerializer(serializers.ModelSerializer):
    """购物车中商品所在的店铺序列化器"""

    class Meta:
        model = Store
        fields = ('id', 'name', 'intro')

class ShopCartCommoditySerializer(serializers.ModelSerializer):
    """购物车商品序列化器"""

    store = ShopCartStoreSerializer()

    class Meta:
        model = Commodity
        fields = ('id', 'commodity_name', 'price', 'favourable_price', 'intro', 'status', 'little_image', 'store')

class ShopCartSkuSerializer(serializers.ModelSerializer):
    """购物车"""

    class Meta:
        model = Sku
        fields = ('id', 'sid', 'price', 'favourable_price', 'name', 'status')


class ShopCartDeleteSerializer(serializers.Serializer):
    """删除购物车序列化器"""
    pk_list = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=False, write_only=True)

    class Meta:
        model = Trolley

    def delete(self):
        user = getattr(self.context.get('request'), 'user')
        rows, _ = self.Meta.model.trolley_.filter(user=user, pk__in=self.validated_data.pop('pk_list')).delete()
        return rows


class ShopCartSerializer(serializers.ModelSerializer):
    """购物车商品序列化器"""

    commodity_info = ShopCartCommoditySerializer(read_only=True, source='commodity')
    sku_info = ShopCartSkuSerializer(read_only=True, source='sku')


    class Meta:
        model = Trolley
        commodity_model = Commodity
        fields = ('pk', 'count', 'commodity', 'sku', 'commodity_info', 'sku_info')
        read_only_fields = ('pk', 'commodity_info', 'sku_info')

    def add(self):
        """向购物车添加商品"""
        credential = {
            'user': getattr(self.context.get('request'), 'user'),
            'commodity': self.validated_data.get('commodity'),
            'count': self.validated_data.get('count', 1),
            'sku': self.validated_data.get('sku')
        }
        self.Meta.model.trolley_.create(**credential)

        # TODO:后续为了进行用户行为的分析，可以记录用户假如购物车的商品，作为行为分析的数据


class CartCountSerializer(serializers.ModelSerializer):
    """购物车的商品数量序列化器"""
    # 购物车中记录的id值
    tid = serializers.IntegerField(min_value=1, write_only=True)

    # 购物车中对应商品的sku的id值
    sid = serializers.IntegerField(min_value=1, write_only=True)

    # 购买的商品数量
    count = serializers.IntegerField(min_value=1, max_value=999999, write_only=True)

    class Meta:
        model = Trolley
        sku_model = Sku
        fields = ('tid', 'sid', 'count')

    def validate_tid(self, value):
        """校验购物车记录是否存在"""
        try:
            return self.Meta.model.trolley_.get(pk=value)
        except self.Meta.model.DoesNotExist:
            raise DataNotExist()

    def validate_sid(self, value):
        """
        校验sku记录是否存在
        返回优惠的价格
        """
        try:
            sku_dict = self.Meta.sku_model.objects.values('favourable_price').filter(pk=value).first()
        except self.Meta.sku_model.DoesNotExist:
            raise DataNotExist()
        else:
            return sku_dict.get('favourable_price')

    def modify(self):
        """
        更新购物车中该商品记录的数量
        同时计算数量在sku中对应的总价格，返回给客户端
        :return decimal price
        """

        credential = {
            'trolley': self.validated_data.pop('tid'),
            'price': self.validated_data.pop('sid'),
            'count': self.validated_data.pop('count')
        }
        trolley = credential.get('trolley')
        trolley.count = credential.get('count')
        trolley.save()
        return credential.get('count') * credential.pop('price')
