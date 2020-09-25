# -*- coding: utf-8 -*- 
# @Time : 2020/5/28 11:26 
# @Author : 司云中 
# @File : favorites_serializers.py
# @Software: PyCharm
from Shop_app.models.commodity_models import Commodity
from Shopper_app.models.shopper_models import Store
from User_app.models.user_models import Collection, Address
from e_mall.loggings import Logging
from rest_framework import serializers

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')



class CommoditySerializer(serializers.ModelSerializer):

    class Meta:
        model = Commodity
        exclude = ('store', 'shopper', 'onshelve_time', 'unshelve_time')

class StoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Store
        fields = '__all__'


class FavoritesSerializer(serializers.ModelSerializer):
    """收藏夹序列化器"""

    # 收藏商铺
    store_pk = serializers.IntegerField(required=False, write_only=True)

    # 收藏商品
    commodity_pk = serializers.CharField(required=False, write_only=True)

    commodity = CommoditySerializer(read_only=True)    # 必须和外键名同名

    store = StoreSerializer(read_only=True)


    def validate(self, attrs):
        if not any([attrs.get('store_pk', None), attrs.get('commodity_pk', None)]):
            raise serializers.ValidationError('店铺和商品二选一')
        return attrs

    @staticmethod
    def get_store_commodity(validated_data):
        """获取store/commodity对象"""
        store_pk = validated_data.get('store_pk', None)
        commodity_pk = validated_data.get('commodity_pk', None)
        store = None
        commodity = None
        if store_pk and Store.store_.filter(pk=store_pk).exists():
            store =  Store.store_.filter(pk=store_pk)
        if commodity_pk and Commodity.commodity_.filter(pk=commodity_pk).exists():
            commodity = Commodity.commodity_.filter(pk=commodity_pk)
        return store, commodity

    class Meta:
        model = Collection
        fields =('pk', 'commodity_pk', 'store_pk', 'commodity', 'store')
        read_only_fields = ('commodity_name', 'pk')

