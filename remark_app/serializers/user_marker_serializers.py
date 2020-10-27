# -*- coding: utf-8 -*- 
# @Time : 2020/5/29 13:29 
# @Author : 司云中 
# @File : user_marker_serializers.py
# @Software: PyCharm
import math

from remark_app.models.remark_models import Remark
from remark_app.signals import check_remark_action
from Emall.loggings import Logging
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

    is_add = serializers.BooleanField(write_only=True)  # 是否追加评论

    is_update = serializers.BooleanField(write_only=True)   # 是否可以追加评论

    def validate(self, attrs):
        """
        如果is_add为True，此时只有redis中满足添加的条件时，才能操作数据库
        如果is_update为True，此时只有redis中满足更新的条件时，才能操作数据库
        防止直接调用接口，大量的不满足条件的请求，hit数据库
        :param attrs:
        :return:
        """
        if attrs.get('is_add') == attrs.get('is_update'):
            raise serializers.ValidationError('不可同时更新和添加！')
        elif attrs.get('is_add'):
            result = check_remark_action.send(
                sender=Remark,
                pk=attrs.get('pk'),
                user=self.context.get('request').user,
                is_remark=True,
                is_action=False
            )
            if result[0][1] == True:  # 当redis中bitmap对应的offset的bit为1,表示评论过了
                raise serializers.ValidationError('您已经评论过了')
            else:
                return attrs
        elif attrs.get('is_update'):
            result = check_remark_action.send(
                sender=Remark,
                pk=attrs.get('pk'),
                user=self.context.get('request').user,
                is_remark=False,
                is_action=True
            )
            if result[0][1] == False:  # 当redis中bitmap对应的offset的bit为0,表示尚未评论
                raise serializers.ValidationError('您尚未评论！')
            else:
                return attrs


    def get_grade_human(self, obj):
        return obj.get_grade_display()

    class Meta:
        model = Remark
        fields = ('is_add','is_update',
                  'commodity_name', 'grade_human', 'grade', 'reward_content', 'reward_time', 'price', 'category', 'image')



