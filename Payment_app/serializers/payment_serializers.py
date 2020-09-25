# -*- coding: utf-8 -*- 
# @Time : 2020/6/1 10:03 
# @Author : 司云中 
# @File : payment_serializers.py
# @Software: PyCharm
import time

from django.contrib.auth.models import User

from Order_app.models.order_models import Order_basic, Order_details
from Payment_app.models.Alipay_models import PayInformation
from Shop_app.models.commodity_models import Commodity
from User_app.models.user_models import Address
from e_mall.loggings import Logging
from rest_framework import serializers

from django.db import transaction, DatabaseError

common_logger = Logging.logger('django')

order_logger = Logging.logger('order_')


class AddressSuccessSerializer(serializers.ModelSerializer):
    """地址序列化器（成功支付）"""

    class Meta:
        model = Address
        fields = ('recipients','region', 'phone')

class UserSuccessSerializer(serializers.ModelSerializer):
    """用户序列化器（成功支付）"""

    class Meta:
        model = User
        fields = ('username',)

class CommoditySuccessSerializer(serializers.ModelSerializer):
    """商品序列化器（成功支付）"""

    class Meta:
        model = Commodity
        fields = ('commodity_name', 'image')


class OrderDetailSuccessSerializer(serializers.ModelSerializer):
    """订单细节序列化器（成功支付）"""

    commodity = CommoditySuccessSerializer(read_only=True)

    class Meta:
        model = Order_details
        fields = ('commodity', 'price', 'image')



class OrderBasicSuccessSerializer(serializers.ModelSerializer):
    """订单基本序列化器（成功支付）"""

    user = UserSuccessSerializer(read_only=True, many=True)
    address = AddressSuccessSerializer(read_only=True, many=True)
    order_details = OrderDetailSuccessSerializer(read_only=True, many=True)

    class Meta:
        model = Order_basic
        fields = ('orderId', 'user', 'address', 'order_details')


class PaymentSerializer(serializers.ModelSerializer):
    """支付序列化器"""

    order = OrderBasicSuccessSerializer

    @staticmethod
    def compute_total_price(total_price, exist_bonus=None, bonus_id=None):
        if not exist_bonus:
            return total_price
        else:
            return total_price-exist_bonus

    @staticmethod
    def compute_generate_order_details(request, order_basic, **kwargs):
        """compute the base information of these goods with appointed counts"""
        commodity_id_counts = {}  # use dict store map between id and counts
        common_logger.info(type(request.session.get('commodity_list')))
        session_commodity_list = request.session.get('commodity_list', None)
        session_counts_list = request.session.get('counts_list', None)

        # 防止接口攻击
        if session_commodity_list is None or session_counts_list is None:
            raise Exception

        total_price = 0  # 订单总价
        try:
            # generate dict
            for pk, counts in zip(session_commodity_list, session_counts_list):
                commodity_id_counts[pk] = counts
            commodity = Commodity.commodity_.select_related('store', 'shopper').filter(
                pk__in=session_commodity_list)  # one hit database
            for value in commodity:
                order_details = Order_details.order_details_.create(belong_shopper=value.shopper,
                                                                    commodity=value,
                                                                    order_basic=order_basic,
                                                                    price=value.discounts * value.price,
                                                                    commodity_counts=commodity_id_counts.get(value.pk),
                                                                    )
                total_price += value.price * value.discounts * commodity_id_counts.get(value.pk)
            total_price = PaymentSerializer.compute_total_price(total_price)
        except Exception as e:
            order_logger.error(e)
            return None, 0
        else:
            return total_price, sum(session_counts_list)

    @staticmethod
    def get_address(request):
        return Address.address_.get(user=request.user, default_address=True)

    @staticmethod
    def choice_payment(payment=None):
        """choice the form of payment"""
        if payment is None:
            return 3  # 支付宝
        else:
            return payment

    @staticmethod
    def create_order(request, user, **data):
        """create new order"""
        try:
            # 是否需要开启事务提交?
            with transaction.atomic():
                orderId = int(round(time.time() * 1000000))
                address = PaymentSerializer.get_address(request)
                # 默认支付方式为支付宝
                payment = PaymentSerializer.choice_payment()
                order_basic = Order_basic.order_basic_.create(consumer=user, region=address, orderId=orderId,
                                                              payment=payment, **data)
                total_price, total_counts = PaymentSerializer.compute_generate_order_details(request, order_basic,
                                                                                             **data)
                if total_price is None:
                    raise DatabaseError
                # update total_price
                order_basic.total_price = total_price
                order_basic.save()
        except DatabaseError as e:  # rollback
            common_logger.info(e)
            return None
        else:
            return order_basic

    @staticmethod
    def update(user, **data):
        """when the transaction is successful,update trade_number,status,checked,remarked or any other"""
        try:
            orderId = data.pop('orderId')
            update_rows = Order_basic.order_basic_.filter(consumer=user, orderId=orderId).update(**data)
            return True if update_rows else False
        except Exception as e:
            order_logger.error(e)
            return False

    class Meta:
        model = PayInformation
        fields = ('trade_id', 'generate_time', 'order')
