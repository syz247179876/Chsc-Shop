# -*- coding: utf-8 -*- 
# @Time : 2020/5/9 22:53 
# @Author : 司云中 
# @File : AddressSerializerApi.py
# @Software: PyCharm
from Shop_app.models.commodity_models import Commodity
from User_app.models.user_models import Address
from django.db import transaction, DatabaseError
from e_mall.loggings import Logging
from rest_framework import serializers

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class AddressSerializers(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['pk', 'recipients', 'region', 'address_tags', 'phone', 'default_address']

    def add_or_edit_address(self, queryset, instance, validated_data):
        """
        创建新的地址
        如果第一次创建地址，则将第一个地址设置为默认地址
        """
        address_ = queryset.count()
        try:
            default_address = True if address_ == 0 else False
            address = self.Meta.model.address_.create(
                user=instance,
                default_address=default_address,
                recipients=validated_data['recipients'],
                region=validated_data['region'],
                address_tags=validated_data['address_tags'],
                phone=validated_data['phone'],
            )
        except Exception as e:
            consumer_logger.error(e)
            return None
        else:
            return address

    @staticmethod
    def update_default_address(queryset, pk):
        """修改默认地址"""
        try:
            common_logger.info(pk)
            if int(pk) <= 0:
                raise serializers.ValidationError({'pk': ['必须为正整数']})
            # 开启事务
            with transaction.atomic():
                addresses = queryset
                addresses.filter(default_address=True).update(default_address=False)  # 全置为False
                addresses.filter(pk=pk).update(default_address=True)  # 重设默认地址
                return True
        except DatabaseError:
            return False

    def update_address(self, queryset, validated_data, pk):
        """修改地址"""
        if int(pk) < 0:
            raise serializers.ValidationError('必须为正整数')
        instance = queryset.get(pk=pk)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        try:
            instance.save()
        except Exception as e:
            consumer_logger.error(e)
            return False
        else:
            return True

    @staticmethod
    def delete_address(queryset, pk):
        """删除某个选定的地址"""
        if int(pk) < 0:
            raise serializers.ValidationError('必须为正整数')
        try:
            queryset.get(pk=pk).delete()
        except Address.DoesNotExist as e:
            consumer_logger.error(e)
            return False
        else:
            return True
