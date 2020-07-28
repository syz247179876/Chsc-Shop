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
    pk = serializers.IntegerField()

    class Meta:
        model = Address
        fields = ['pk', 'recipients', 'region', 'address_tags', 'phone']

    def add_or_edit_address(self, instance, validated_data):
        """
        创建新的地址
        如果第一次创建地址，则将第一个地址设置为默认地址
        """
        address_ = self.Meta.model.address_.filter(user=instance).count()
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

    def update_default_address(self, queryset, validated_data):
        """修改默认地址"""
        try:
            # 开启事务
            with transaction.atomic():
                addresses = queryset
                addresses.filter(default_address=True).update(default_address=False)  # 全置为False
                addresses.filter(pk=validated_data['pk']).update(default_address=True)  # 重设默认地址
                return True
        except DatabaseError:
            return False

    def update_address(self, validated_data):
        """修改地址"""
        instance = self.Meta.model.address_.get(pk=validated_data['pk'])
        for key, value in validated_data.items():
            setattr(instance, key, value)
        try:
            instance.save()
        except Exception as e:
            consumer_logger.error(e)
            return False
        else:
            return True

    def delete_address(self, queryset, validated_data):
        """删除某个选定的地址"""
        try:
            queryset.get(pk=validated_data['pk']).delete()
        except DatabaseError as e:
            consumer_logger.error(e)
            return False
        else:
            return True
