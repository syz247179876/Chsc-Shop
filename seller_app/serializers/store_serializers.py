# -*- coding: utf-8 -*-
# @Time  : 2021/2/18 下午4:49
# @Author : 司云中
# @File : store_serializers.py
# @Software: Pycharm

from rest_framework import serializers

from Emall.exceptions import DataFormatError
from seller_app.models import Store


class SellerStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ('id', 'name', 'intro')
        read_only_fields = ('id')
        extra_kwargs = {
            'intro': {'require': False}
        }

    def add(self):
        """创建店铺"""
        intro =  self.validated_data.pop('intro', None)
        if not intro or len(intro) > 128:
            raise DataFormatError()
        credential = {
            'name': self.validated_data.pop('name'),
            'intro': intro
        }
        self.Meta.model.objects.create(**credential)

