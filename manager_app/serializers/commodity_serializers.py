# -*- coding: utf-8 -*-
# @Time  : 2021/2/15 下午7:39
# @Author : 司云中
# @File : commodity_serializers.py
# @Software: Pycharm
from django.db import DataError
from rest_framework import serializers
from rest_framework.fields import JSONField

from Emall.exceptions import DataFormatError
from shop_app.models.commodity_models import CommodityCategory, CommodityGroup


class SellerCommoditySerializer(serializers.ModelSerializer):
    """商家管理商品序列化器"""

    class Meta:
        model = CommodityCategory
        fields = ('id', 'name', '')


class CommodityCategoryCreateSerializer(serializers.Serializer):
    """
    商家管理商品分类序列化器
    格式:

    {
    "category":[
        {
            "name":"商品总类",
            "intro":"商品总类",
            "pre_id":1
        },
        {
            "name":"裤子",
            "intro":"裤子总类",
            "pre_id":1
        },
        {
            "name":"衣服",
            "intro":"衣服总类",
            "pre_id":1
        }
      ]
    }
    """

    category = JSONField()

    def create_category(self):
        """创建种类"""
        category = self.validated_data.get('category')
        try:
            CommodityCategory.commodity_category_.bulk_create(
                [CommodityCategory(**item) for item in category]
            )
        except DataError:
            raise DataFormatError('数据类型错误或数据格式非法')


class CommodityCategoryDeleteSerializer(serializers.Serializer):
    """用于商品类别删除功能的序列化器"""
    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


class CommodityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommodityCategory
        fields = ('pk', 'name', 'intro', 'thumbnail', 'sort', 'pre')


    def update_category(self):
        """更新商品类别"""
        self.Meta.model.commodity_category_.filter(pk=self.validated_data.pop('pk')).update(**self.validated_data)


class CommodityGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommodityGroup
        fields = ('pk', 'name', 'status')
        read_only_fields = ('pk', )

    def update_group(self):
        """修改商品分组"""
        pk = self.validated_data.pop('pk')
        credential = {
            'name':self.validated_data.pop('name'),
            'status':self.validated_data.pop('status')
        }
        self.Meta.model.commodity_group_.filter(pk=pk).update(**credential)

    def add_group(self):
        """添加商品分组"""
        credential = {
            'name': self.validated_data.pop('name'),
            'status': self.validated_data.pop('status')
        }
        self.Meta.model.commodity_group_.create(**credential)


class CommodityGroupDeleteSerializer(serializers.Serializer):
    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)