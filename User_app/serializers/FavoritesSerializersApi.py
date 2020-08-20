# -*- coding: utf-8 -*- 
# @Time : 2020/5/28 11:26 
# @Author : 司云中 
# @File : FavoritesSerializersApi.py 
# @Software: PyCharm
from Shop_app.models.commodity_models import Commodity
from e_mall.loggings import Logging
from rest_framework import serializers

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class FavoritesSerializer(serializers.ModelSerializer):
    """收藏夹序列化器"""

    # 收藏商铺
    store = serializers.IntegerField(source='store', required=False)

    # 商铺名
    store_name = serializers.CharField(source='store.store_name')

    # 收藏商品
    commodity = serializers.CharField(source='commodity', required=False)

    attention = serializers.IntegerField(source='store.attention')

    shop_grade = serializers.DecimalField(source='store.shop_grade', max_digits=2,
                                          decimal_places=1)

    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = Commodity
        fields = ('store', 'commodity', 'pk', 'store_name', 'commodity_name', 'price', 'intro',
                  'category', 'status', 'discounts', 'sell_counts', 'image', 'shop_grade', 'attention')

        read_only_fields = (
        'pk', 'store_name', 'commodity_name', 'price', 'intro', 'category', 'status', 'discounts', 'sell_counts',
        'image', 'shop_grade', 'attention')
