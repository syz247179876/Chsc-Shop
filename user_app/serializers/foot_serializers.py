# -*- coding: utf-8 -*- 
# @Time : 2020/5/28 14:03 
# @Author : 司云中 
# @File : foot_serializers.py
# @Software: PyCharm
from shop_app.models.commodity_models import Commodity
from Emall.loggings import Logging
from rest_framework import serializers

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class FootSerializer(serializers.ModelSerializer):
    """the serializer of Foot(足迹)"""

    pk = serializers.IntegerField(write_only=True) #  商品 id
    timestamp = serializers.SerializerMethodField()  # 只读特性,将任何类型数据添加到序列化表示中

    def get_timestamp(self, obj):
        """为每个足迹追加时间戳"""
        timestamp_dict = self.context.get('timestamp')
        return timestamp_dict.get(obj.pk)

    def validate_pk(self, value):
        """校验pk字段是否存在   """
        if not Commodity.commodity_.filter(pk=value).exists():
            raise serializers.ValidationError('商品信息无效')
        return value

    class Meta:
        model = Commodity
        fields = ('id', 'timestamp', 'commodity_name', 'price', 'status', 'discounts', 'image', 'pk')
        read_only_fields = (
            'id', 'commodity_name', 'price', 'status', 'discounts', 'image')
