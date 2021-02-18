# -*- coding: utf-8 -*-
# @Time  : 2021/2/17 下午10:38
# @Author : 司云中
# @File : commodity_serializers.py
# @Software: Pycharm
from django.db import DatabaseError
from rest_framework import serializers

from Emall.exceptions import DataFormatError, SqlServerError, DataNotExist
from shop_app.models.commodity_models import Commodity, CommodityCategory, CommodityGroup, Freight, SkuProps, SkuValues
from django.db.transaction import atomic


class CommodityCategorySerializer(serializers.ModelSerializer):
    """商品类别序列化器"""

    subs = serializers.SerializerMethodField()

    class Meta:
        model = CommodityCategory
        fields = '__all__'

    def get_subs(self, obj):
        if obj.pre:
            return CommodityCategorySerializer(obj.pre, many=True).data
        else:
            return None



class SellerCommoditySerializer(serializers.ModelSerializer):
    """商家操作商品模型序列化器"""

    category_list = serializers.SerializerMethodField()

    class Meta:
        model = Commodity
        category_model = CommodityCategory
        fields = ('pk', 'commodity_name', 'price', 'favourable_price', 'details', 'intro', 'category_id', 'group_id',
                  'status', 'onshelve_time', 'unshelve_time', 'stock', 'big_image', 'little_image',
                  'freight_id', 'category_list')
        read_only_fields = ('pk', 'category_list')

    def get_category_list(self, obj):
        """获取全部的序列化器"""
        category = self.Meta.category_model.objects.all()
        return CommodityCategorySerializer(category, many=True).data

    def add_commodity(self):
        """商家添加商品"""
        credential = self.get_credential
        self.Meta.model.commodity_.create(**credential)

    def update_commodity(self):
        """商家修改商品"""
        pk = self.validated_data.pop('pk')
        credential = self.get_credential
        self.Meta.model.commodity_.filter(pk=pk).update(**credential)

    @property
    def get_credential(self):
        try:
            category = CommodityCategory.objects.get(pk=self.validated_data.pop('category_id'))
            group = CommodityGroup.commodity_group_.get(pk=self.validated_data.pop('group_id'))
            freight = Freight.freight_.get(pk=self.validated_data.pop('freight_id'))
        except CommodityCategory.DoesNotExist:
            raise DataFormatError()
        except CommodityGroup.DoesNotExist:
            raise DataFormatError()
        except Freight.DoestNotExist:
            raise DataFormatError()
        else:
            return {
                'category': category,
                'group': group,
                'freight': freight,
                'commodity_name': self.validated_data.pop('commodity_name'),
                'price': self.validated_data.pop('price'),
                'favourable_price': self.validated_data.pop('favourable_price'),
                'details': self.validated_data.pop('details'),
                'intro': self.validated_data.pop('category_id'),
                'status':self.validated_data.pop('status')
            }


class SellerCommodityDeleteSerializer(serializers.Serializer):

    class Meta:
        model = Commodity

    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


    def delete_commodity(self):
        """商家删除商品"""
        self.Meta.model.commodity_.filter(pk__in=self.validated_data.pop('pk_list')).delete()


class SkuPropSerializer(serializers.ModelSerializer):
    """sku 属性:[属性值,]序列化器"""

    sku_values = serializers.ListField(child=serializers.CharField(max_length=20), allow_empty=False)

    class Meta:
        model = SkuProps
        values_model = SkuValues
        fields = ('pk', 'name', 'sku_values')
        read_only_fields = ('pk', )


    def add(self):
        """添加sku属性规格和值"""
        credential = {
            'name': self.validated_data.pop('name'),
            'sku_values': self.validated_data.pop('sku_values')
        }
        try:
            with atomic(): # 开启事务
                prop = self.Meta.model.objects.create(name=credential.pop('name'))
                self.Meta.values_model.objects.bulk_create([
                    self.Meta.values_model.objects.create(value=value, prop=prop) for value in credential.pop('sku_values')
                ])
        except DatabaseError():
            raise SqlServerError()

    def modify(self):
        """修改商品属性规格和值"""
        credential = {
            'name':self.validated_data.pop('name'),
            'sku_values': self.validated_data.pop('sku_values')
        }
        try:
            with atomic():
                # 先全部删除,然后重新添加
                prop = self.Meta.model.objects.get(name=credential.pop('name'))
                self.Meta.values_model.objects.filter(prop=prop).delete()
                self.Meta.values_model.objects.bulk_create([
                    self.Meta.values_model.objects.create(value=value, prop=prop) for value in
                    credential.pop('sku_values')
                ])
        except DatabaseError():
            raise SqlServerError()

        except self.Meta.model.DoesNotExist:
            raise DataNotExist()


class SkuPropsDeleteSerializer(serializers.Serializer):
    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

    class Meta:
        model = SkuProps

    def delete(self):
        """删除商品属性规格和值"""
        self.Meta.model.objects.filter(pk__in=self.validated_data.pop('pk_list')).delete()

