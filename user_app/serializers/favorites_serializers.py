# -*- coding: utf-8 -*- 
# @Time : 2020/5/28 11:26 
# @Author : 司云中 
# @File : favorites_serializers.py
# @Software: PyCharm
import datetime

from Emall.exceptions import DataNotExist, DataFormatError
from Emall.loggings import Logging
from user_app.model.collection_models import Commodity, Collection

from rest_framework import serializers

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class CommoditySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commodity
        exclude = ('commodity_name', 'onshelve_time', 'unshelve_time', 'intro', 'status', 'price', 'favourable_price')


class FavoritesSerializer(serializers.ModelSerializer):
    """收藏夹序列化器"""

    # 收藏商品
    commodity_pk = serializers.IntegerField(write_only=True, required=False)

    # 收藏某些商品
    commodity_pk_list = serializers.ListSerializer(child=serializers.IntegerField(min_value=1), allow_empty=False,
                                                   required=False, write_only=True)

    cid = serializers.IntegerField(source='commodity.pk', read_only=True)

    commodity_name = serializers.CharField(source='commodity.commodity_name', read_only=True)

    onshelve_time = serializers.DateTimeField(source='commodity.onshelve_time', read_only=True)

    unshelve_time = serializers.DateTimeField(source='commodity.unshelve_time', read_only=True)

    intro = serializers.CharField(source='commodity.intro', read_only=True)

    status = serializers.BooleanField(source='commodity.status', read_only=True)

    price = serializers.DecimalField(max_digits=9, decimal_places=2, source='commodity.price', read_only=True)

    favourable_price = serializers.DecimalField(max_digits=9, decimal_places=2, source='commodity.favourable_price',
                                                read_only=True)

    class Meta:
        model = Collection
        commodity_model = Commodity
        fields = (
            'pk', 'cid', 'commodity_pk', 'commodity_name', 'onshelve_time', 'unshelve_time', 'intro', 'status', 'price',
            'favourable_price', 'commodity_pk_list')
        read_only_fields = ('pk',)

    def validate_commodity_pk_list(self, value):
        """验证收藏的一系列商品的id值是否存在"""
        queryset = self.Meta.commodity_model.commodity_.filter(pk__in=value)
        if not queryset.exists():
            raise DataNotExist()
        else:
            return queryset

    def validate_commodity_pk(self, value):
        """验证收藏的商品id值是否存在"""
        queryset = self.Meta.commodity_model.commodity_.filter(pk=value)
        if not queryset.exists():
            raise DataNotExist()
        else:
            return queryset.first()

    def add(self, request):
        """添加商品到收藏夹"""
        commodity = self.validated_data.pop('commodity_pk', None)
        if not commodity:
            raise DataFormatError('数据缺失')
        # 如果用户已经收藏过该商品
        if self.Meta.model.objects.filter(user=request.user, commodity=commodity).exists():
            return None
        # 创建新的收藏记录
        return self.Meta.model.objects.create(user=request.user, commodity=commodity,
                                              collect_time=datetime.datetime.now())

    def bulk_add(self, request):
        """添加一系列商品到收藏夹"""
        commodity_list = self.validated_data.pop('commodity_pk_list', None)
        if not commodity_list:
            raise DataFormatError('数据缺失')
        self.Meta.model.objects.bulk_create([
            self.Meta.model(user=request.user, commodity=obj, collect_time=datetime.datetime.now()) for obj in
            commodity_list
        ])
