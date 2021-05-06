# -*- coding: utf-8 -*-
# @Time  : 2021/2/18 下午4:49
# @Author : 司云中
# @File : store_serializers.py
# @Software: Pycharm
from django.contrib.auth import get_user_model
from django.db import DatabaseError, transaction
from rest_framework import serializers

from Emall.exceptions import DataFormatError, SqlServerError, DataExisted, DataNotExist
from manager_app.models import Role
from seller_app.models import Store, Seller

User = get_user_model()


class SellerStoreSerializer(serializers.ModelSerializer):
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
            # 判断该用户是否已经开店
            if self.Meta.seller_model.objects.filter(user=user).exists():
                raise DataExisted()
            with transaction.atomic():
                store = self.Meta.model.objects.create(**credential)  # 创建店铺
                self.Meta.seller_model.objects.create(user=user, store=store, role=role)  # 创建商家
                user.is_seller = True  # 将该用户升级成商家,具备商家权限
                user.save(force_update=True)
        except self.Meta.role_model.DoesNotExist:
            raise DataNotExist()
        except DatabaseError:
            raise SqlServerError()


class SellerUserDisplaySerializer(serializers.ModelSerializer):
    """商家个人信息序列化器"""

    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'phone', 'is_seller', 'is_active',
                  'birthday', 'sex', 'head_image', 'date_joined')


class SellerStoreDisplaySerializer(serializers.ModelSerializer):
    """商家店铺信息序列化器"""

    type = serializers.CharField(source='get_type_display', read_only=True)

    rank = serializers.CharField(source='get_rank_display', read_only=True)

    class Meta:
        model = Store
        fields = '__all__'


class SellerRoleDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        exclude = ['permission']


class SellerDisplaySerializer(serializers.ModelSerializer):
    """商家个人信息+店铺信息序列化器"""

    user = SellerUserDisplaySerializer()

    store = SellerStoreDisplaySerializer()

    role = SellerRoleDisplaySerializer()

    class Meta:
        model = Seller
        fields = '__all__'


class SellerUpdateInfoSerializer(serializers.ModelSerializer):
    """
    商家更新个人信息序列化器
    """

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'birthday', 'sex')

    def modify(self):
        user = self.context.get('request').user
        user.username = self.validated_data.get('username', None) or user.username
        user.email = self.validated_data.get('email', None) or user.email
        user.phone = self.validated_data.get('phone', None) or user.phone
        user.sex = self.validated_data.get('sex', None) or user.sex
        user.save(update_fields=['username', 'email', 'phone', 'sex'])


class SellerUpdateStoreSerializer(serializers.ModelSerializer):
    """
    商家更新店铺相关信息序列化器
    """

    class Meta:
        model = Store
        seller_model = Seller
        fields = ('pk', 'name', 'intro', 'province')
        extra_kwargs = {
            'province':{
                'required':True
            }
        }


    def modify(self):
        pk = self.context.get('request').data.get('pk', None)
        if not pk:
            raise DataFormatError('缺少数据')
        user = self.context.get('request').user
        queryset = self.Meta.model.objects.select_related('seller__user').filter(pk=pk, seller__user=user)
        if queryset.count() == 0:
            raise DataNotExist()
        return queryset.update(**self.validated_data)

