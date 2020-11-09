# -*- coding: utf-8 -*- 
# @Time : 2020/5/30 10:38 
# @Author : 司云中 
# @File : shopcart_serializers.py
# @Software: PyCharm
import datetime
import json

from rest_framework import serializers

from Emall.loggings import Logging
from shop_app.models.commodity_models import Commodity
from user_app.model.seller_models import Store
from user_app.model.trolley_models import Trolley

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class CommoditySerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    def get_price(self, obj):
        """获取打折后的价格"""
        return obj.price * obj.discounts

    class Meta:
        model = Commodity
        fields = ('pk', 'commodity_name', 'price')


class StoreSerializer(serializers.ModelSerializer):
    commodity = CommoditySerializer(many=True, read_only=True)  # 一条trolley中的一个store对应的是多个commodity

    class Meta:
        model = Store
        fields = ('pk', 'store_name',)


class ShopCartSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)  # 一条trolley记录对应一个store

    pk_list = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=None, max_length=99999,
                                    write_only=True, required=False)  # 删除的pk列表

    # commodity_dict = serializers.DictField(child=serializers.CharField(max_length=20), allow_empty=None,
    #                                        write_only=True, required=False)  # 添加商品到购物车的商品信息

    provision = serializers.JSONField(required=False)

    def validate_provision(self, value):
        """
        验证commodity_dict字段
        :param value:dict
        :return:
        """
        """
        格式验证：
        {
            "provision":{
                "pk":1,
                "count":3,
                "label":{
                    "pk":"2",
                    "content":"湛蓝色-大号"
                }
            }
        }
        """

        if all([value.get('pk', None), value.get('count', None), value.get('label', None)]):
            label = value.get('label')
            if all([label.get('pk', None), label.get('content', None)]):
                try:
                    # 必须统一类型，确保接口安全
                    return {
                        'pk': int(value.get('pk')),
                        'count': int(value.get('count')),
                        'label': {
                            'pk': int(label.get('pk')),
                            'content': str(label.get('content'))
                        }
                    }
                except ValueError:
                    raise serializers.ValidationError('参数类型不正确')
        raise serializers.ValidationError('参数格式不正确')

    def validate(self, attrs):
        if self.context.get('request').method == 'DELETE':
            if not attrs.get('pk_list', None):
                raise serializers.ValidationError('参数不符合要求')
        elif self.context.get('request').method == 'POST':
            if not attrs.get('provision', None):
                raise serializers.ValidationError('参数不符合要求')
        return attrs

    def label_exist(self, obj, label_pk, label_content):
        """
        判断选择是否存在商品的总label中
        :param obj: Commodity object
        :param label_pk: 选择标签pk
        :param label_choice: 选择标签content
        :return:
        """
        labels = json.loads(obj.label)
        return True if label_pk in labels and labels[label_pk] == label_content else False

    def compute_price(self, obj, count):
        """
        计算商品价格
        :return:
        """
        price = obj.price * obj.discounts
        return price * count

    def add_trolley(self, validated_data):
        """添加商品到购物车"""
        user = self.context.get('request').user
        provision = validated_data.get('provision')
        commodity_pk = provision.get('pk')
        commodity_count = provision.get('count')
        label = provision.get('label')
        try:
            commodity_obj = Commodity.commodity_.select_related('store').get(
                pk=commodity_pk)  # 这里不计算是否还有库存，结算时再计算是否还有库存
            is_exist = self.label_exist(commodity_obj, label.pop('pk'), label.pop('content'))
            if is_exist:
                price = self.compute_price(commodity_obj, commodity_count)
                time = datetime.datetime.now()
                trolley_obj = self.Meta.model.trolley_.create(user=user, commodity=commodity_obj,
                                                              store=commodity_obj.store,
                                                              time=time, count=commodity_count, price=price)
                if trolley_obj:
                    return True
            raise serializers.ValidationError({'error': '不存在选择标签'})
        except Commodity.DoesNotExist:
            return False

    class Meta:
        model = Trolley
        fields = ('pk', 'store', 'time', 'pk_list', 'provision')
        read_only_fields = ('pk', 'store', 'time')
