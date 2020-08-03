# -*- coding: utf-8 -*- 
# @Time : 2020/5/26 20:10 
# @Author : 司云中 
# @File : OrderSerializerApi.py
# @Software: PyCharm
import math

from Order_app.models.order_models import Order_details, Order_basic
from Shop_app.models.commodity_models import Commodity
from User_app.models.user_models import Address
from django.db import transaction, DatabaseError
from e_mall.loggings import Logging
from rest_framework import serializers

common_logger = Logging.logger('django')

order_logger = Logging.logger('order_')


# 订单显示所需序列化器

class ChoiceDisplayField(serializers.ChoiceField):

    def to_representation(self, value):
        """针对value(choice)转成我们需要的格式"""
        return self.choices[value]


class OrderBasicSerializer(serializers.ModelSerializer):
    """订单序列化容器"""

    order_details = serializers.SerializerMethodField()  # 递归嵌套序列化器，订单细节

    status = serializers.SerializerMethodField()  # 获取可读的status

    def get_status(self, obj):
        return obj.get_status_display()

    def get_order_details(self, obj):
        """嵌套order_details"""
        order_details = Order_details.order_details_.filter(order_basic=obj.pk)
        if order_details.count() > 0:
            return OrderDetailsSerializer(order_details, many=True).data
        return ''

    @staticmethod
    def get_order_and_page(user, **kwargs):
        """
        lazy load with specific paging and status from HTPRequest.GET
        add order into redis
        """
        try:
            cur_page = int(kwargs.get('page')[0])  # from request.GET
            limit = 4 if 'limit' not in kwargs else int(kwargs.get('limit')[0])  # every time show four order
            status = '0' if 'limit' not in kwargs else kwargs.get('status')[0]
            total_instances = Order_basic.order_basic_.select_related('region').filter(consumer=user) \
                .order_by('-generate_time')
            counts = total_instances.count()
            start = (cur_page - 1) * limit
            end = cur_page * limit
            limit_instances = total_instances[start:end] if status == '0' else total_instances.filter(status=status)[
                                                                               start:end]  # 选择特定订单状态的limit个instances
            max_pages = math.ceil(counts / limit)
            return limit_instances, max_pages
        except Exception as e:
            common_logger.info(e)
            return None, 0

    @staticmethod
    def delete_order(**kwargs):
        """delete order from redis"""
        try:
            orderId = int(kwargs.get('orderId')[0])
            with transaction.atomic():
                Order_basic.order_basic_.get(orderId=orderId).delete()
        except DatabaseError as e:
            order_logger.error(e)
            return False
        else:
            return True

    class Meta:
        model = Order_basic
        fields = ('orderId', 'trade_number', 'total_price', 'commodity_total_counts', 'generate_time', 'status',
                  'order_details', 'generate_time')


class OrderDetailsSerializer(serializers.ModelSerializer):
    """
    订单商品详情序列化容器
    The serializer of Order_details which used to combine with Order_basic
    """

    commodity = serializers.SerializerMethodField()  # 商品细节

    def get_commodity(self, obj):
        commodity = Commodity.commodity_.filter(order_details=obj.pk)
        if len(commodity) > 0:
            return CommoditySerializer(commodity, many=True).data
        return ''

    class Meta:
        model = Order_details
        fields = ('price', 'commodity', 'commodity_counts')


class CommoditySerializer(serializers.ModelSerializer):
    """ the serializer of commodity which used to combine with Order_details"""

    store_name = serializers.CharField(source='store.store_name')

    class Meta:
        model = Commodity
        fields = ('store_name', 'store_name', 'commodity_name', 'intro', 'category', 'discounts', 'freight', 'image')


class PageSerializer(serializers.Serializer):
    """页数序列器"""

    page = serializers.IntegerField()

    data = serializers.SerializerMethodField()

    @property
    def serializer_class(self):
        """data serializer"""
        return self.context.get('serializer')

    def get_data(self, obj):
        instances = self.context.get('instances', None)
        context = self.context.get('context', {})
        return self.serializer_class(instances, context=context, many=True).data


class Page:
    """the instance of page"""

    def __init__(self, page):
        self.page = page


# 订单提交所需序列化器

class OrderCommitSerialiizer(serializers.Serializer):
    pass


class OrderAddressSerializer(serializers.ModelSerializer):

    @staticmethod
    def get_address(user):
        """get address of current consumer"""
        try:
            return Address.address_.filter(user=user)
        except Address.DoesNotExist:
            return None


class OrderCommoditySerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    counts = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    def get_price(self, obj):
        """序列化商品优惠价"""
        return float(obj.price * obj.discounts)

    def get_total_price(self, obj):
        """序列化商品数量*优惠价"""
        return float(obj.price * obj.discounts * self.get_counts(obj))

    def get_counts(self, obj):
        return self.context.get(obj.pk)

    @staticmethod
    def get_commodity(commodity_list):
        """get address of current consumer"""
        try:
            return Commodity.commodity_.select_related('store').filter(pk__in=commodity_list)
        except Commodity.DoesNotExist:
            return None

    class Meta:
        model = Commodity
        fields = ['commodity_name', 'pk', 'price', 'intro', 'category', 'freight', 'total_price', 'image',
                  'discounts_intro', 'stock', 'counts']
