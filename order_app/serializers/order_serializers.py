# -*- coding: utf-8 -*- 
# @Time : 2020/5/26 20:10 
# @Author : 司云中 
# @File : order_serializers.py
# @Software: PyCharm
import datetime
import json

from Emall.exceptions import DataNotExist, SqlServerError
from order_app.models.order_models import OrderDetail, OrderBasic
from shop_app.models.commodity_models import Commodity, Sku
from user_app.model.trolley_models import Trolley
from user_app.models import Address
from django.db import transaction, DatabaseError
from Emall.loggings import Logging
from rest_framework import serializers
from decimal import Decimal

common_logger = Logging.logger('django')

order_logger = Logging.logger('order_')


# 订单显示所需序列化器

# class ChoiceDisplayField(serializers.ChoiceField):
#
#     def to_representation(self, value):
#         """针对value(choice)转成我们需要的格式"""
#         return self.choices[value]


class OrderSkuSerializer(serializers.ModelSerializer):
    """与订单相关的SKU信息"""

    properties = serializers.SerializerMethodField()

    def get_properties(self, obj):
        """反序列化"""
        return json.loads(obj.properties)

    class Meta:
        model = Sku
        fields = ('pk', 'sid', 'favourable_price', 'properties', 'image', 'name')
        read_only_fields = ('pk', 'sid', 'favourable_price', 'properties', 'image', 'name')


class CommoditySerializer(serializers.ModelSerializer):
    """ 与订单细节有关的商品序列化器"""

    # 店铺名
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Commodity
        fields = ('commodity_name', 'intro', 'little_image', 'store_name')


class OrderDetailsSerializer(serializers.ModelSerializer):
    """
    订单商品详情序列化容器
    The serializer of OrderDetail which used to combine with OrderBasic
    """

    commodity = CommoditySerializer()

    sku = OrderSkuSerializer()

    class Meta:
        model = OrderDetail
        fields = ('commodity', 'sku', 'counts')


class OrderBasicSerializer(serializers.ModelSerializer):
    """订单序列化容器"""

    order_details = OrderDetailsSerializer(many=True, read_only=True)

    status = serializers.SerializerMethodField(required=False)  # 获取可读的status

    pk_list = serializers.ListField(required=False, write_only=True, allow_empty=False,
                                    child=serializers.IntegerField())  # 订单号集合

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = OrderBasic
        fields = ('order_id', 'trade_number', 'total_price', 'total_counts', 'generate_time', 'status',
                  'order_details', 'pk_list')
        read_only_fields = ('order_id', 'trade_number', 'total_price', 'total_counts', 'generate_time', 'status',
                  'order_details')


class OrderCreateSerializer(serializers.ModelSerializer):
    sku_dict = serializers.DictField(child=serializers.IntegerField(max_value=9999),
                                     allow_empty=False, write_only=True)  # sku的id-数量字典
    payment = serializers.CharField(write_only=True)

    def validate_payment(self, value):
        if value not in (str(i) for i in range(1, 5)):
            raise serializers.ValidationError('付款类型不正确')
        return value

    def compute_order_details(self, queryset):
        """计算初始订单的商品总价格和总数量"""

        total_price = 0  # 订单总价
        sku_dict = self.validated_data['sku_dict']
        if queryset.count() < len(sku_dict):
            raise DataNotExist()
        for value in queryset:
            # 创建详细订单表
            total_price += (value.favourable_price * sku_dict.get(str(value.pk)))
        return total_price, sum(sku_dict.values())

    @staticmethod
    def generate_orderid(pk):
        """产生唯一订单号"""
        now = datetime.datetime.now()
        return '{third_year}{month}{day}{hour}{pk}{minute}{second}{microsecond}'.format(
            third_year=str(now.year)[2:], month=str(now.month), day=str(now.day),
            hour=str(now.hour), minute=str(now.minute), second=str(now.second),
            microsecond=str(now.microsecond), pk=str(pk)
        )

    @staticmethod
    def get_address(user):
        return Address.address_.get(user=user, default_address=True)

    def create_order(self, user, redis):
        """创建初始订单"""
        credential = {
            'order_id': '',
            'user': self.context.get('request').user,
            'address': None,
            'voucher': None,
            'payment': self.validated_data.get('payment'),
            'total_counts': 0,
            'total_price': 0,
            'favourable_price': 0,
            'true_price': 0
        }
        try:
            credential['address'] = self.get_address(user)
            pk = user.pk
            credential['order_id'] = self.generate_orderid(pk)  # 产生订单号
            queryset = Sku.objects.filter(
                pk__in=[int(pk) for pk in self.validated_data.get('sku_dict').keys()]).select_related('commodity')
            total_price, total_counts = self.compute_order_details(queryset)  # 计算总价和总数量
            # 重新修改订单表总数量
            credential['total_price'] = total_price
            credential['total_counts'] = total_counts
            # TODO 目前没做优惠卷模块，真实价格按照总价格来
            credential['favourable_price'] = total_price
            credential['true_price'] = total_price
            sku_dict = self.validated_data.get('sku_dict')
            with transaction.atomic():
                order_basic = OrderBasic.order_basic_.create(**credential)  # 创建初始订单
                OrderDetail.order_detail_.bulk_create([
                    OrderDetail(commodity=sku.commodity, order_basic=order_basic, sku=sku, counts=sku_dict.get(key)) for
                    sku, key in zip(queryset, sku_dict)
                ])
        except DatabaseError as e:  # rollback
            order_logger.error(e)
            raise SqlServerError()
        else:
            redis.set_order_expiration(order_basic.pk)  # 设置订单过期时间
            return order_basic

    class Meta:
        model = OrderBasic
        fields = ('sku_dict', 'payment')


class OrderConfirmSerializer(serializers.ModelSerializer):
    """订单确认序列化器"""

    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False, write_only=True)

    commodity_name = serializers.CharField(source='commodity.commodity_name', read_only=True)

    cid = serializers.IntegerField(source='commodity.pk', read_only=True)

    intro = serializers.CharField(source='commodity.intro', read_only=True)

    store_name = serializers.CharField(source='commodity.store.name', read_only=True)

    sku = OrderSkuSerializer(read_only=True)

    is_free = serializers.BooleanField(source='commodity.freight.is_free', read_only=True)

    class Meta:
        model = Trolley
        fields = ('pk', 'cid', 'pk_list', 'store_name', 'commodity_name', 'count', 'time', 'sku', 'intro', 'is_free')
        read_only_fields = ('pk', 'cid', 'store_name', 'commodity_name', 'count', 'time', 'sku', 'intro', 'is_free')


class OrderCommoditySerializer(serializers.ModelSerializer):
    """订单提交序列化器"""

    total_price = serializers.SerializerMethodField(read_only=True, required=False)
    commodity_counts_dict = serializers.DictField(child=serializers.IntegerField(max_value=9999),
                                                  allow_empty=False)
    store_commodity_dict = serializers.DictField(child=serializers.IntegerField(max_value=9999999),
                                                 allow_empty=False)
    price = serializers.SerializerMethodField(read_only=True, required=False)

    def get_price(self, obj):
        """序列化商品优惠价"""
        return float(obj.price * obj.discounts)

    def get_total_price(self, obj):
        """序列化商品数量*优惠价"""
        return float(obj.price * obj.discounts * self.get_counts(obj))

    def get_counts(self, obj):
        return self.context.get(obj.pk)

    class Meta:
        model = Commodity
        fields = ['commodity_name', 'pk', 'price', 'intro', 'category', 'freight', 'total_price', 'big_image',
                  'discounts_intro', 'commodity_counts_dict', 'store_commodity_dict']
        read_only_fields = ['commodity_name', 'pk', 'price', 'intro', 'category', 'freight', 'total_price',
                            'total_price', 'big_image', 'discounts_intro']


class OrderSellerAddressSerializer(serializers.ModelSerializer):
    """与商家+订单有关的地址序列化器"""

    class Meta:
        model = Address
        fields = ('recipient', 'province', 'region', 'phone')


class OrderSellerSerializer(serializers.ModelSerializer):
    """与商家有关的订单序列化器"""

    commodity_name = serializers.CharField(source='commodity.commodity_name')

    order_id = serializers.CharField(source='order_basic.order_id')

    status = serializers.CharField(source='order_basic.get_status_display')

    is_checked = serializers.CharField(source='order_basic.is_checked')

    efficient_time = serializers.CharField(source='order_basic.efficient_time')

    recipient = serializers.CharField(source='order_basic.address.recipient')

    province = serializers.CharField(source='order_basic.address.province')

    region = serializers.CharField(source='order_basic.address.region')

    phone = serializers.CharField(source='order_basic.address.phone')

    sku_favourable_price = serializers.DecimalField(source='sku.favourable_price', max_digits=9, decimal_places=2)

    sku_image = serializers.CharField(source='sku.image')

    sku_name = serializers.CharField(source='sku.name')

    sku_properties = serializers.SerializerMethodField()

    def get_sku_properties(self, obj):
        """反序列化"""
        return ''.join((key+":"+value+";" for key,value in json.loads(obj.sku.properties).items()))

    class Meta:
        model = OrderDetail
        fields = ('pk', 'commodity_name', 'order_id', 'status' ,'is_checked', 'efficient_time', 'recipient',
                  'province', 'region', 'phone', 'sku_favourable_price', 'sku_properties', 'sku_image', 'sku_name')
