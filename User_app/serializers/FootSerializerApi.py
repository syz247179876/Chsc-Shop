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

    pk = serializers.IntegerField(write_only=True)
    timestamp = serializers.SerializerMethodField()

    def get_timestamp(self, obj):
        timestamp_dict = self.context.get('timestamp')
        return timestamp_dict.get(obj.pk)

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
        fields = ('id', 'timestamp', 'commodity_name', 'price', 'intro',
                  'category', 'status', 'discounts', 'image', 'pk')
        read_only_fields = (
            'id', 'commodity_name', 'price', 'intro', 'category', 'status', 'discounts', 'image')
