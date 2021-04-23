# -*- coding: utf-8 -*-
# @Time : 2020/5/30 10:38
# @Author : 司云中
# @File : shopcart_serializers.py
# @Software: PyCharm
import datetime
import json

from rest_framework import serializers

from Emall.exceptions import DataTypeError, DataFormatError, LabelError, SqlServerError, DataNotExist
from Emall.loggings import Logging
from seller_app.models import Store
from shop_app.models.commodity_models import Commodity, Sku
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

    # 总记录条数
    total = serializers.IntegerField(read_only=True)


    class Meta:
        model = Trolley
        commodity_model = Commodity
        fields = ('pk', 'count', 'commodity', 'sku', 'total')
        read_only_fields = ('pk', 'total')

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

# class ShopCartSerializer(serializers.ModelSerializer):
#
#     pk_list = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=None, max_length=99999,
#                                     write_only=True, required=False)  # 删除的pk列表
#
#     # commodity_dict = serializers.DictField(child=serializers.CharField(max_length=20), allow_empty=None,
#     #                                        write_only=True, required=False)  # 添加商品到购物车的商品信息
#
#     provision = serializers.JSONField(required=False)
#
#     def validate_provision(self, value):
#         """
#         验证commodity_dict字段
#         :param value:dict
#         :return:
#         """
#         """
#         格式验证：
#         {
#             "provision":{
#                 "pk":1,
#                 "count":3,
#                 "label":{
#                     "pk":"2",
#                     "content":"湛蓝色-大号"
#                 }
#             }
#         }
#         """
#
#         if all([value.get('pk', None), value.get('count', None), value.get('label', None)]):
#             label = value.get('label')
#             if all([label.get('pk', None), label.get('content', None)]):
#                 try:
#                     # 必须统一类型，确保接口安全
#                     return {
#                         'pk': int(value.get('pk')),
#                         'count': int(value.get('count')),
#                         'label': {
#                             'pk': int(label.get('pk')),
#                             'content': str(label.get('content'))
#                         }
#                     }
#                 except ValueError:
#                     raise DataTypeError()
#         raise DataFormatError()
#
#     def validate(self, attrs):
#         if self.context.get('request').method == 'DELETE':
#             if not attrs.get('pk_list', None):
#                 raise DataFormatError('参数不符合要求')
#         elif self.context.get('request').method == 'POST':
#             if not attrs.get('provision', None):
#                 raise DataFormatError('参数不符合要求')
#         return attrs
#
#     def label_exist(self, obj, label_pk, label_content):
#         """
#         判断选择的标签是否存在商品的总label中
#         :param obj: Commodity object
#         :param label_pk: 选择标签pk
#         :param label_choice: 选择标签content
#         :return:
#         """
#         labels = json.loads(obj.label)
#         return True if label_pk in labels and labels[label_pk] == label_content else False
#
#     def compute_price(self, obj, count):
#         """
#         计算商品价格
#         :return:
#         """
#         price = obj.price * obj.discounts
#         return price * count
#
#     def add_trolley(self, validated_data):
#         """添加商品到购物车"""
#         user = self.context.get('request').user
#         provision = validated_data.get('provision')
#         commodity_pk = provision.get('pk')
#         commodity_count = provision.get('count')
#         label = provision.get('label')
#         try:
#             commodity_obj = Commodity.commodity_.select_related('store').get(
#                 pk=commodity_pk)  # 这里不计算是否还有库存，结算时再计算是否还有库存
#             is_exist = self.label_exist(commodity_obj, label.pop('pk'), label.pop('content'))
#             if is_exist: # 标签存在
#                 price = self.compute_price(commodity_obj, commodity_count)
#                 time = datetime.datetime.now()
#                 self.Meta.model.trolley_.create(user=user, commodity=commodity_obj,
#                                                               store=commodity_obj.store,
#                                                               time=time, count=commodity_count, price=price)
#                 return True
#             raise LabelError('不存在选择标签')
#         except Commodity.DoesNotExist:
#             raise SqlServerError()
#
#     class Meta:
#         model = Trolley
#         fields = ('pk', 'store', 'time', 'pk_list', 'provision')
#         read_only_fields = ('pk', 'store', 'time')
