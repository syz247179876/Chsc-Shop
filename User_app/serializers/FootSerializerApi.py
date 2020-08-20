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
        """为每个足迹追加时间戳"""
        timestamp_dict = self.context.get('timestamp')
        return timestamp_dict.get(obj.pk)

    def validate_pk(self, value):
        if not Commodity.commodity_.all().exists():
            raise serializers.ValidationError('商品信息无效')
        return value

    class Meta:
        model = Commodity
        fields = ('id', 'timestamp', 'commodity_name', 'price', 'intro',
                  'category', 'status', 'discounts', 'image', 'pk')
        read_only_fields = (
            'id', 'commodity_name', 'price', 'intro', 'category', 'status', 'discounts', 'image')
