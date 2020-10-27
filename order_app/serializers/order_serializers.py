# -*- coding: utf-8 -*- 
# @Time : 2020/5/26 20:10 
# @Author : 司云中 
# @File : order_serializers.py
# @Software: PyCharm
import datetime

from order_app.models.order_models import Order_details, Order_basic
from shop_app.models.commodity_models import Commodity
from user_app.models import Address
from django.db import transaction, DatabaseError
from Emall.loggings import Logging
from rest_framework import serializers

common_logger = Logging.logger('django')

order_logger = Logging.logger('order_')


# 订单显示所需序列化器

# class ChoiceDisplayField(serializers.ChoiceField):
#
#     def to_representation(self, value):
#         """针对value(choice)转成我们需要的格式"""
#         return self.choices[value]


class CommoditySerializer(serializers.ModelSerializer):
    """ the serializer of commodity which used to combine with Order_details"""

    store_name = serializers.CharField(source='store.store_name')

    class Meta:
        model = Commodity
        fields = ('store_name', 'store_name', 'commodity_name', 'intro', 'category', 'discounts', 'freight', 'image')


class OrderDetailsSerializer(serializers.ModelSerializer):
    """
    订单商品详情序列化容器
    The serializer of Order_details which used to combine with Order_basic
    """

    commodity = CommoditySerializer()

    # def get_commodity(self, obj):
    #     commodity = Commodity.commodity_.filter(order_details=obj.pk)
    #     if len(commodity) > 0:
    #         return CommoditySerializer(commodity, many=True).data
    #     return ''

    class Meta:
        model = Order_details
        fields = ('price', 'commodity', 'commodity_counts')


class OrderBasicSerializer(serializers.ModelSerializer):
    """订单序列化容器"""

    order_details = OrderDetailsSerializer(many=True, read_only=True)

    status = serializers.SerializerMethodField(required=False)  # 获取可读的status

    list_pk = serializers.ListField(required=False, write_only=True, allow_empty=False,
                                    child=serializers.IntegerField())  # 订单号集合

    def get_status(self, obj):
        return obj.get_status_display()

    # def get_order_details(self, obj):
    #     """嵌套order_details"""
    #     order_details = Order_details.order_details_.filter(order_basic=obj.pk)
    #     if order_details.count() > 0:
    #         return OrderDetailsSerializer(order_details, many=True).data
    #     return ''

    class Meta:
        model = Order_basic
        fields = ('orderId', 'trade_number', 'total_price', 'commodity_total_counts', 'generate_time', 'status',
                  'order_details', 'generate_time', 'list_pk')


class OrderCreateSerializer(serializers.ModelSerializer):
    commodity_dict = serializers.DictField(child=serializers.IntegerField(max_value=9999), allow_empty=False)  # 商品-数量字典
    payment = serializers.CharField()

    def validate_payment(self, value):
        if value not in (str(i) for i in range(1, 5)):
            raise serializers.ValidationError('付款类型不正确')
        return value

    @staticmethod
    def compute_order_details(validated_data, order_basic, **kwargs):
        """计算初始订单的商品价格"""

        total_price = 0  # 订单总价
        commodity_dict = validated_data['commodity_dict']
        try:
            commodity = Commodity.commodity_.select_related('store', 'shopper').filter(
                pk__in=[int(pk) for pk in commodity_dict.keys()])  # one hit database
            for value in commodity:
                # 创建详细订单表
                Order_details.order_details_.create(belong_shopper=value.shopper,
                                                    commodity=value,
                                                    order_basic=order_basic,
                                                    price=value.discounts * value.price,
                                                    commodity_counts=commodity_dict.get(str(value.pk)),
                                                    )
                total_price += value.price * value.discounts * commodity_dict.get(str(value.pk))
        except Exception as e:
            order_logger.error(e)
            return 0, 0
        else:
            return total_price, sum(value for value in commodity_dict.values())

    @staticmethod
    def generate_orderid(pk):
        """产生唯一订单号："""
        now = datetime.datetime.now()
        return '{third_year}{month}{day}{hour}{pk}{minute}{second}{microsecond}'.format(third_year=str(now.year)[2:],
                                                                                        month=str(now.month),
                                                                                        day=str(now.day),
                                                                                        hour=str(now.hour),
                                                                                        minute=str(now.minute),
                                                                                        second=str(now.second),
                                                                                        microsecond=str(
                                                                                            now.microsecond),
                                                                                        pk=str(pk))

    @staticmethod
    def get_address(user):
        return Address.address_.get(user=user, default_address=True)

    def create_order(self, validated_data, user, redis):
        """创建初始订单"""
        try:
            with transaction.atomic():
                pk = user.pk
                orderId = self.generate_orderid(pk)  # 产生订单号
                address = self.get_address(user)
                order_basic = Order_basic.order_basic_.create(consumer=user, region=address, orderId=orderId,
                                                              payment=validated_data.get('payment'))  # 创建初始订单
                total_price, total_counts = self.compute_order_details(validated_data, order_basic)  # 计算总价和总数量
                # 重新修改订单表总数量
                order_basic.total_price = total_price
                order_basic.total_counts = total_counts
                order_basic.save(update_fields=['total_price', 'commodity_total_counts'])
        except DatabaseError as e:  # rollback
            order_logger.error(e)
            return None
        else:
            redis.set_order_expiration(pk)  # 设置订单过期时间
            return order_basic

    class Meta:
        model = Order_basic
        fields = ('commodity_dict', 'payment')


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
        fields = ['commodity_name', 'pk', 'price', 'intro', 'category', 'freight', 'total_price', 'image',
                  'discounts_intro', 'commodity_counts_dict', 'store_commodity_dict']
        read_only_fields = ['commodity_name', 'pk', 'price', 'intro', 'category', 'freight', 'total_price',
                            'total_price', 'image', 'discounts_intro']
