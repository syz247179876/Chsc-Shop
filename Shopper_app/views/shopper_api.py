# -*- coding: utf-8 -*- 
# @Time : 2020/6/1 19:42 
# @Author : 司云中 
# @File : shopper_api.py
# @Software: PyCharm
import datetime

from Shopper_app.redis.shopper_redis import RedisShopperOperation
from Shopper_app.serializers.ShopperSerializerApi import ShopperSerializer
from User_app.views.ali_card_ocr import Interface_identify
from django.contrib.auth.models import User, Permission
from django.db import transaction, DatabaseError
from django.http import Http404
from django.shortcuts import render, redirect
from e_mall.loggings import Logging
from e_mall.response_code import response_code
from rest_framework.response import Response
from rest_framework.views import APIView

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
    def set_shopper_perm(cls, user):
        permissions = Permission.objects.filter(codename__in=cls.permissions_pub)
        for permission in permissions:
            # 增加商家基本权限
            user.user_permissions.add(permission)


class ShopperOperation(APIView):
    redis = RedisShopperOperation.choice_redis_db('redis')  # 选择redis具体db
    serializer_class = ShopperSerializer

    def get_serializer(self, *args, **kwargs):
        """get object of serializer"""
        serializer_class = self.get_serializer_class
        return serializer_class(*args, **kwargs)

    @property
    def get_serializer_class(self):
        return self.serializer_class

    @staticmethod
    def enter_login(request):
        return redirect('/admin')

    @staticmethod
    def enter_register(request):
        return render(request, 'Sregister.html')

    def factory_get(self, request, **data):
        """简单工厂管理登录注册"""
        way_map = {
            'login': 'enter_login',
            'register': 'enter_register'
        }
        func = getattr(self, way_map.get(data.get('way')[0]), None)
        if func is None:
            # 后期改成固定异常页
            return Http404()
        return func(request)

    def get(self, request):
        """进入注册页"""
        data = request.GET
        return self.factory_get(request, **data)

    def verify(self, image, card_type):
        """阿里的接口"""
        identify_instance = Interface_identify(image, card_type)

        # Check whether the identification is successful
        is_success = identify_instance.is_success
        if not is_success:
            return None
        else:
            return identify_instance

    def post(self, request):
        """注册商家"""
        try:
            data = request.data
            verification = data.get('verification')  # 验证码
            email = data.get('user_email')
            image = data.get('image')
            card_type = data.get('card_type', 'face')
            is_checked = self.redis.check_code(email, verification)
            if not is_checked:  # 验证码错误
                return Response(response_code.verification_code_error)
            else:
                phone = data.get('phone')
                existed_str = self.get_serializer_class.check_shopper_existed(email, phone)

                if existed_str == 'email_existed':  # 邮箱被占用
                    return Response(response_code.email_exist)
                elif existed_str == 'phone_existed':  # 手机号被占用
                    return Response(response_code.phone_exist)
                elif existed_str is None:  # 服务器错误
                    return Response(response_code.server_error)
                else:
                    verified_instance = self.verify(image.read(), card_type)  # 身份证识别
                    if verified_instance is None:
                        return Response(response_code.verify_id_card_error)
                    user = self.serializer_class.create_shopper(verified_instance, **data)  # 创建商家
                    if user:
                        Shopper_user_prem.set_shopper_perm(user)  # 分配权限
                        return Response(response_code.register_success)
                    else:
                        return Response(response_code.register_error)
        except Exception as e:
            # shopper_logger.error(e)
            return Response(response_code.server_error)
