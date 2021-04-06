# -*- coding: utf-8 -*- 
# @Time : 2020/5/9 22:53 
# @Author : 司云中 
# @File : address_serializers.py
# @Software: PyCharm
from Emall.exceptions import SqlServerError
from user_app.models import Address
from django.db import transaction, DatabaseError
from Emall.loggings import Logging
from rest_framework import serializers

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class AddressSerializers(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = ['pk', 'recipient', 'region', 'address_tags', 'phone', 'default_address', 'province']

    def add_or_edit_address(self, queryset, instance, validated_data):
        """
        创建新的地址
        如果第一次创建地址，则将第一个地址设置为默认地址
        """
        address_count = queryset.count()
        try:
            default_address = validated_data.get('default_address')

            address = self.Meta.model.address_.create(
                user=instance,
                default_address=default_address,
                recipient=validated_data['recipient'],
                region=validated_data['region'],
                address_tags=validated_data['address_tags'],
                phone=validated_data['phone'],
                province=validated_data['province']
            )
            # 默认地址为True且有其他地址数据集时修改
            if default_address and address_count > 0:
                self.update_default_address(queryset, address.pk)

        except Exception as e:
            consumer_logger.error(e)
            raise SqlServerError()

    @staticmethod
    def update_default_address(queryset, pk):
        """修改默认地址"""
        try:
            # 开启事务
            with transaction.atomic():
                addresses = queryset
                addresses.filter(default_address=True).update(default_address=False)  # 全置为False
                addresses.filter(pk=pk).update(default_address=True)  # 重设默认地址
        except DatabaseError:
            raise SqlServerError()

    @staticmethod
    def update_address(queryset, validated_data, pk):
        """修改地址"""

        try:
            instance = queryset.get(pk=pk)
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()
        except Exception as e:
            consumer_logger.error(e)
            raise SqlServerError()

    @staticmethod
    def delete_address(queryset, pk):
        """删除某个选定的地址"""
        try:
            queryset.get(pk=pk).delete()
        except Address.DoesNotExist as e:
            consumer_logger.error(e)
            raise SqlServerError()
