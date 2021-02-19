# -*- coding: utf-8 -*-
# @Time  : 2021/2/15 下午7:39
# @Author : 司云中
# @File : commodity_serializers.py
# @Software: Pycharm
from django.db import DataError, transaction
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
    "category":
        {
           "pre_id:1,
           "children":[
            {
                "name":"商品总类",
                "intro":"商品总类",
            },
            {
                "name":"裤子",
                "intro":"裤子总类",
            },
            {
                "name":"衣服",
                "intro":"衣服总类",
            }
          ]
        }
    }
    """

    category = JSONField()

    class Meta:
        model = CommodityCategory

    def first_create(self):
        """
        创建最初总类(商品)
        此类别应由最高管理员创建
        """
        data = self.context.get('request').data
        self.Meta.model.objects.first_create(**data)

    def create_category(self):
        """创建种类"""
        category = self.validated_data.get('category')
        children = category.get('children')

        # 如果没有子类
        if not children:
            raise DataFormatError('子类别不能为空')

        # 修改上一个结点类的数据,创建其子类
        try:
            pre_category = self.Meta.model.objects.get(pk=category.get('pre_id'))
            with transaction.atomic():
                # 如果为设置有next,才需设置
                if not pre_category.has_next:
                    pre_category.has_next = True
                    pre_category.save(force_update=True)
                self.Meta.model.objects.bulk_create(
                    [self.Meta.model(pre=pre_category, has_prev=True, **item) for item in category.get('children')]
                )
        except self.Meta.model.DoesNotExist:
            raise DataFormatError()
        except DataError:
            raise DataFormatError('数据类型错误或数据格式非法')


class CommodityCategoryDeleteSerializer(serializers.Serializer):
    """用于商品类别删除功能的序列化器"""
    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


class CommodityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommodityCategory
        fields = ('pk', 'name', 'intro', 'thumbnail', 'sort', 'pre')  # pre会反序列化为model实例
        read_only_fields = ('pk',)

    def update_category(self):
        """
        更新商品类别
        需先校验前驱结点必须正确
        """
        pre = self.validated_data.pop('pre', None)
        if not pre:
            raise DataFormatError('缺少数据')
        try:
            self.Meta.model.objects.filter(pk=self.context.get('request').data.pop('pk'), pre=pre).update(
                **self.validated_data)
        except self.Meta.model.DoesNotExist:
            raise DataFormatError('数据内容错误')


class CommodityGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommodityGroup
        fields = ('pk', 'name', 'status')
        read_only_fields = ('pk',)

    def update_group(self):
        """修改商品分组"""
        pk = self.context.get('request').data.pop('pk')
        credential = {
            'name': self.validated_data.pop('name'),
            'status': self.validated_data.pop('status')
        }
        return self.Meta.model.objects.filter(pk=pk).update(**credential)

    def add_group(self):
        """添加商品分组"""
        credential = {
            'name': self.validated_data.pop('name'),
            'status': self.validated_data.pop('status')
        }
        self.Meta.model.objects.create(**credential)


class CommodityGroupDeleteSerializer(serializers.Serializer):
    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
