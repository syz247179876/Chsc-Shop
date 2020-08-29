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
    GRADE_CHOICE = (
        (1, '一星好评'),
        (2, '二星好评'),
        (3, '三星好评'),
        (4, '四星好评'),
        (5, '五星好评'),
    )
    grade = serializers.ChoiceField(choices=GRADE_CHOICE, write_only=True)

    grade_human = serializers.SerializerMethodField(read_only=True)

    commodity_name = serializers.CharField(source='commodity.commodity_name', read_only=True)

    price = serializers.IntegerField(source='commodity.price', read_only=True)

    category = serializers.CharField(source='commodity.category', read_only=True)

    image = serializers.ImageField(source='commodity.image', read_only=True)

    def get_grade_human(self, obj):
        return obj.get_grade_display()

    class Meta:
        model = Remark
        fields = ['commodity_name', 'grade_human', 'grade', 'reward_content', 'reward_time', 'price', 'category', 'image']



