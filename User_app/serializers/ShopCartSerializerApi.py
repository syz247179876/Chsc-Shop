# -*- coding: utf-8 -*- 
# @Time : 2020/5/30 10:38 
# @Author : 司云中 
# @File : ShopCartSerializerApi.py 
# @Software: PyCharm

from Shop_app.models.commodity_models import Commodity
from Shopper_app.models.shopper_models import Store
from User_app.models.trolley_models import Trolley
from User_app.serializers.PageSerializerApi import PageSerializer
from django.db import transaction, DatabaseError
from e_mall.loggings import Logging
from rest_framework import serializers

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


# class ShopCartSerializer(serializers.ModelSerializer):
#     goods = serializers.SerializerMethodField()
#     store_name = serializers.SerializerMethodField()
#
#     @staticmethod
#     def get_stores(store_list):
#         """generate store instances based on store_list"""
#         try:
#             return Store.store_.filter(pk__in=store_list)
#         except Exception as e:
#             consumer_logger.error(e)
#             return None
#
#     def get_store_name(self, obj):
#         if isinstance(obj, Store):
#             return obj.store_name
#         else:
#             return ''
#
#     def get_goods(self, obj):
#         if isinstance(obj, Store):
#             store_and_commodity = self.context.get('store_and_commodity')  # 获取对应的store和commodity_id的字典映射
#             commodity_and_store = self.context.get('commodity_and_store')
#             commodity_and_price = self.context.get('commodity_and_price')
#             instances_id_list = store_and_commodity[obj.pk]
#             instances = Commodity.commodity_.filter(pk__in=instances_id_list)
#             if instances.count() > 0:
#                 return CommoditySerializer(instances, context={'commodity_and_store': commodity_and_store,
#                                                                'commodity_and_price': commodity_and_price},
#                                            many=True).data
#             return ''
#         return ''
#
#     class Meta:
#         model = Store
#         fields = ['id', 'store_name', 'shop_grade', 'province', 'goods']
#
#
# class CommoditySerializer(serializers.ModelSerializer):
#     """the serializer of commodity under the ShopCart function"""
#     counts = serializers.SerializerMethodField()
#     total_price = serializers.SerializerMethodField()
#
#     def get_total_price(self, obj):
#         if isinstance(obj, Commodity):
#             id_dict = self.context.get('commodity_and_price')  # 通过字典映射获取对应commodity的price
#             return id_dict[obj.pk]
#         return ''
#
#     def get_counts(self, obj):
#         if isinstance(obj, Commodity):
#             id_dict = self.context.get('commodity_and_store')  # 通过字典映射获取对应commodity的counts
#             return id_dict[obj.pk]
#         return ''
#
#     class Meta:
#         model = Commodity
#         exclude = ['store', 'shopper', 'details', 'onshelve_time', 'unshelve_time', 'sell_counts']


class CommoditySerializer(serializers.ModelSerializer):

    price = serializers.SerializerMethodField()

    def get_price(self, obj):
        """获取打折后的价格"""
        return obj.price * obj.discounts

    class Meta:
        model = Commodity
        fields = ('pk', 'commodity_name','price')


class StoreSerializer(serializers.ModelSerializer):

    commodity = CommoditySerializer(many=True, read_only=True)   # 一条trolley中的一个store对应的是多个commodity

    class Meta:
        model = Store
        fields = ('pk', 'store_name',)

class ShopCartSerializer(serializers.ModelSerializer):

    store = StoreSerializer(read_only=True)   # 一条trolley记录对应一个store

    pk_list = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=None,max_length=99999, write_only=True)   # 删除的pk列表

    class Meta:
        model = Trolley
        fields = ('pk', 'store', 'time', 'pk_list')
        read_only_fields = ('pk', 'store', 'time')