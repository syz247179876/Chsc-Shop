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
    """the serializer of favorites(收藏夹）"""
    store_name = serializers.CharField(source='store.store_name')

    attention = serializers.IntegerField(source='store.attention')

    shop_grade = serializers.DecimalField(source='store.shop_grade', max_digits=2,
                                          decimal_places=1)

    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.get_status_display()

    @staticmethod
    def get_favorites(commodity_list, **kwargs):
        """
        get instance(queryset) of model,
        lazy load with specific paging and status from HTPRequest.GET
        :param commodity_list:商品id列表
        :param data: Querydict
        :return:
        """
        try:
            return Commodity.commodity_.select_related('store').filter(pk__in=commodity_list)
        except Exception as e:
            consumer_logger.error(e)
            return None

    class Meta:
        model = Commodity
        fields = ['pk', 'store_name', 'commodity_name', 'price', 'intro',
                  'category', 'status', 'discounts', 'sell_counts', 'image', 'shop_grade', 'attention']
