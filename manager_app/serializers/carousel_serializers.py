# -*- coding: utf-8 -*-
# @Time  : 2021/4/6 下午9:21
# @Author : 司云中
# @File : carousel_serializers.py
# @Software: Pycharm

from rest_framework import serializers

from Emall.exceptions import DataFormatError
from shop_app.models.commodity_models import Carousel


class ManagerCarouselSerializer(serializers.ModelSerializer):
    """管理轮播图序列化器"""

    class Meta:
        model = Carousel
        fields = ('pk', 'picture', 'url', 'sort', 'type')
        read_only_fields = ('pk',)

    def add(self):
        """增加轮播图"""
        self.Meta.model.objects.create(**self.validated_data)

    def modify(self):
        """修改轮播图"""
        pk = self.context.get('request').data.get('pk')
        if not pk:
            raise DataFormatError('缺少数据')
        return self.Meta.model.objects.filter(pk=pk).update(**self.validated_data)


class DeleteCarouselSerializer(serializers.ModelSerializer):
    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

    class Meta:
        model = Carousel
        fields = ('pk_list',)

    def delete(self):
        """删除轮播图"""
        return self.Meta.model.objects.filter(pk__in=self.validated_data.pop('pk_list')).delete()

