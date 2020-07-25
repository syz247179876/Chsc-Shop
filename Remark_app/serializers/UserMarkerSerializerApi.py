# -*- coding: utf-8 -*- 
# @Time : 2020/5/29 13:29 
# @Author : 司云中 
# @File : UserMarkerSerializerApi.py 
# @Software: PyCharm
import math

from Remark_app.models.remark_models import Remark
from e_mall.loggings import Logging
from rest_framework import serializers

common_logger = Logging.logger('django')

evaluate_logger = Logging.logger('evaluate_')


class ChoiceDisplayField(serializers.ChoiceField):

    def to_representation(self, value):
        """针对value(choice)转成我们需要的格式"""
        return self.choices[value]


class UserMarkerSerializer(serializers.ModelSerializer):
    grade = serializers.SerializerMethodField()

    commodity_name = serializers.CharField(source='commodity.commodity_name')

    price = serializers.IntegerField(source='commodity.price')

    category = serializers.CharField(source='commodity.category')

    image = serializers.ImageField(source='commodity.image')

    @property
    def context(self):
        """extra context"""
        return super().context

    def get_grade(self, obj):
        return obj.get_grade_display()

    @staticmethod
    def get_remark_and_page(user, **kwargs):
        try:
            limit = int(kwargs.get('limit')[0]) if 'limit' in kwargs else 5
            page = int(kwargs.get('page')[0])
            start = (page - 1) * limit
            end = page * limit
            counts = Remark.remark_.select_related('commodity').filter(consumer=user).count()
            instances = Remark.remark_.select_related('commodity').filter(consumer=user)[start:end]
            page = math.ceil(counts / limit)
            return instances, page
        except Exception as e:
            evaluate_logger.error(e)
            return None

    class Meta:
        model = Remark
        fields = ['commodity_name', 'grade', 'reward_content', 'reward_time', 'price', 'category', 'image']


class PageSerializer(serializers.Serializer):
    """页数序列器"""

    page = serializers.IntegerField()

    data = serializers.SerializerMethodField()

    @property
    def serializer_class(self):
        """data serializer"""
        return self.context.get('serializer')

    def get_data(self, obj):
        instances = self.context.get('instances')
        return self.serializer_class(instances, many=True).data


class Page:
    """the instance of page"""

    def __init__(self, page):
        self.page = page
