# -*- coding: utf-8 -*- 
# @Time : 2020/5/28 14:03 
# @Author : 司云中 
# @File : FootSerializerApi.py 
# @Software: PyCharm
from Shop_app.models.commodity_models import Commodity
from e_mall.loggings import Logging
from rest_framework import serializers

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class FootSerializer(serializers.ModelSerializer):
    """the serializer of Foot(足迹)"""

    status = serializers.SerializerMethodField(read_only=True)
    pk = serializers.IntegerField()

    def get_status(self, obj):
        return obj.get_status_display()

    def validate_pk(self, value):
        if not Commodity.commodity_.all().exists():
            raise serializers.ValidationError('商品信息无效')
        return value

    @staticmethod
    def get_foot(commodity_list, **kwargs):
        """
        get instance(queryset) of Commodity,
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
        fields = ['commodity_name', 'price', 'intro',
                  'category', 'status', 'discounts', 'image']
