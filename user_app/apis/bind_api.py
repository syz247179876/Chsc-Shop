# -*- coding: utf-8 -*-
# @Time  : 2021/1/11 下午5:22
# @Author : 司云中
# @File : bind_api.py
# @Software: Pycharm
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Emall.exceptions import SqlServerError, CodeError
from Emall.loggings import Logging
from Emall.response_code import response_code, BIND_SUCCESS
from user_app.redis.user_redis import RedisUserOperation
from user_app.serializers.bind_email_phone_serializers import BindPhoneOrEmailSerializer
consumer_logger = Logging.logger('consumer_')

class BindEmailOrPhone(GenericAPIView):
    """
    绑定（改绑）用户邮箱或者手机号
    需发送验证码验证
    """

    permission_classes = [IsAuthenticated]

    redis = RedisUserOperation.choice_redis_db('redis')  # 选择配置文件中的redis

    serializer_class = BindPhoneOrEmailSerializer

    @staticmethod
    def bind_phone(cache, instance, validated_data):
        """改绑手机号"""
        is_existed = validated_data['is_existed']
        code = validated_data['code']
        new_phone = validated_data['phone']
        if is_existed:
            # 旧手机接受验证码
            old_phone = validated_data['old_phone']
            is_success = cache.check_code(old_phone, code)
        else:
            # 新手机中核对验证码
            is_success = cache.check_code(new_phone, code)
        if is_success:
            instance.phone = new_phone
            try:
                instance.save()
            except Exception as e:
                consumer_logger.error(e)
                return False
            else:
                return True
        return False

    @staticmethod
    def bind_email(cache, instance, validated_data):
        """改绑邮箱"""
        is_existed = validated_data['is_existed']
        code = validated_data['code']
        new_email = validated_data['email']
        if is_existed:
            # 旧邮箱接受验证码
            old_email = validated_data['old_email']
            is_success = cache.check_code(old_email, code)
        else:
            # 新邮箱中核对验证码
            is_success = cache.check_code(new_email, code)
        if is_success:
            instance.email = new_email
            try:
                instance.save()
            except Exception as e:
                consumer_logger.error(e)
                raise SqlServerError()
        raise CodeError()  # 验证码校验错误

    def factory(self, way, validated_data, instance):
        """简单工厂管理手机号和邮箱的改绑"""
        func_list = {
            'email': 'bind_email',
            'phone': 'bind_phone',
        }
        func = func_list.get(way)
        bind = getattr(self, func)
        return bind(self.redis, instance, validated_data)

    def put(self, request):
        """改绑OR绑定用户的手机或者邮箱"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 校验成功
        way = serializer.validated_data.get('way')
        self.factory(way, serializer.validated_data, request.user)
        # 改绑成功
        return Response(response_code.result(BIND_SUCCESS,'绑定成功'))
