# -*- coding: utf-8 -*-
# @Time  : 2021/2/18 下午4:49
# @Author : 司云中
# @File : store_serializers.py
# @Software: Pycharm
from django.contrib.auth import get_user_model
from django.db import DatabaseError, transaction
from rest_framework import serializers

from Emall.exceptions import DataFormatError, SqlServerError
from manager_app.models import Role
from seller_app.models import Store, Seller


class SellerStoreSerializer(serializers.ModelSerializer):
    User = get_user_model()
    class Meta:
        model = Store
        seller_model = Seller
        role_model = Role
        fields = ('id', 'name', 'intro')
        read_only_fields = ('id',)
        extra_kwargs = {
            'intro': {'required': False}
        }

    def create_store(self):
        """创建店铺"""
        intro = self.validated_data.pop('intro', None)
        if not intro or len(intro) > 128:
            raise DataFormatError()
        credential = {
            'name': self.validated_data.pop('name'),
            'intro': intro
        }
        try:
            role = self.Meta.role_model.objects.get(role_name="商家角色")
            user = self.context.get('request').user
            with transaction.atomic():
                store = self.Meta.model.objects.create(**credential)  # 创建店铺
                self.Meta.seller_model.objects.create(user=user, store=store, role=role)  # 创建商家
                user.is_seller = True # 将该用户升级成商家,具备商家权限
                user.save(force_update=True)
        except DatabaseError():
            raise SqlServerError()
