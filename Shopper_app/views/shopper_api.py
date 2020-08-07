# -*- coding: utf-8 -*- 
# @Time : 2020/6/1 19:42 
# @Author : 司云中 
# @File : shopper_api.py
# @Software: PyCharm
from rest_framework import status

from Shopper_app.redis.shopper_redis import RedisShopperOperation
from Shopper_app.serializers.ShopperSerializerApi import ShopperSerializer
from User_app.views.ali_card_ocr import Interface_identify
from django.contrib.auth.models import User, Permission
from e_mall.loggings import Logging
from e_mall.response_code import response_code
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

common_logger = Logging.logger('django')

shopper_logger = Logging.logger('shopper_')


class Shopper_user_prem:
    """设置权限"""
    permissions_pub = [
        'view_remark',
        'add_remark_reply',
        'change_remark_reply',
        'delete_remark_reply',
        'view_goodsby',
        'view_goodstype',
        'view_promotion',
        'add_promotion',
        'change_promotion',
        'delete_promotion',
        'add_commodity',
        'change_commodity',
        'delete_commodity',
        'view_commodity',
        'change_store',
        'view_store',
        'view_shoppers',
        'change_shoppers',
        'view_order_basic',
        'change_order_basic',
        'view_order_details',
        'view_logistic',
        # 'view_notification',
        # 'change_notification',
        # 'delete_notification',
    ]

    @classmethod
    def add_shopper_perm(cls, user):
        """添加商家基本权限"""
        permissions = Permission.objects.filter(codename__in=cls.permissions_pub)
        for permission in permissions:
            # 增加商家基本权限
            user.user_permissions.add(permission)


class ShopperOperation(GenericAPIView):
    """店家操作"""

    redis = RedisShopperOperation.choice_redis_db('redis')  # 选择redis具体db

    serializer_class = ShopperSerializer

    def check_code(self, validated_data):
        """验证码验证"""
        return self.redis.check_code(validated_data.get('phone'), validated_data.get('code'))

    def post(self, request):
        """商家注册"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # if not self.check_code(serializer.validated_data):
        #     return Response(response_code.verification_code_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        user = serializer.create(serializer.validated_data)  # 创建用户
        if user:
            Shopper_user_prem.add_shopper_perm(user)  # 分配权限
            return Response(response_code.create_shopper_success, status=status.HTTP_200_OK)
        else:
            return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
