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
    """the serializers of Model -- Address"""

    class Meta:
        model = Address
        fields = ['recipients', 'region', 'address_tags', 'phone']

    def add_or_edit_address(self, user, validated_data):
        """create new address instance"""
        ModelClass = self.Meta.model
        address_ = Address.address_.filter(user=user).count()
        try:
            default_address = True if address_ == 0 else False
            address = ModelClass.address_.create(
                user=user,
                default_address=default_address,
                recipients=validated_data['recipients'],
                region=validated_data['region'],
                address_tags=validated_data['address_tags'],
                phone=validated_data['phone'],
            )
        except Exception as e:
            common_logger.info(str(e))
            return None
        else:
            return address

    @staticmethod
    def update_default(instance, validated_data):
        """edit information of address"""
        """for key, value in validated_data.items():
            setattr(instance, key, value)"""
        instance.default_address = True
        try:
            with transaction.atomic():
                instance.save()
        except DatabaseError:
            return None
        else:
            return instance

    @staticmethod
    def update_edit(instance, validated_data):
        """update default of address instance with using pk"""
        for key, value in validated_data.items():
            setattr(instance, key, value)
        try:
            with transaction.atomic():
                instance.save()
        except DatabaseError:
            return None
        else:
            return instance
