# -*- coding: utf-8 -*-
# @Time  : 2021/2/17 下午10:38
# @Author : 司云中
# @File : commodity_serializers.py
# @Software: Pycharm

from rest_framework import serializers

from Emall.exceptions import DataFormatError
from shop_app.models.commodity_models import Commodity, CommodityCategory, CommodityGroup, Freight


class SellerCommoditySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commodity
        fields = ('pk', 'commodity_name', 'price', 'favourable_price', 'details', 'intro', 'category_id', 'group_id',
                  'status', 'onshelve_time', 'unshelve_time', 'sell_counts', 'stock', 'big_image', 'little_image',
                  'freight_id')
        read_only_fields = ('pk', )

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
            category = CommodityCategory.commodity_category_.get(pk=self.validated_data.pop('category_id'))
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
            }


class SellerCommodityDeleteSerializer(serializers.Serializer):

    class Meta:
        model = Commodity

    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


    def delete_commodity(self):
        """商家删除商品"""
        self.Meta.model.commodity_.filter(pk__in=self.validated_data.pop('pk_list')).delete()
