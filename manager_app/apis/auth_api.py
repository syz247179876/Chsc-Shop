# -*- coding: utf-8 -*-
# @Time  : 2021/2/9 下午10:44
# @Author : 司云中
# @File : auth_api.py
# @Software: Pycharm

from django.contrib.auth import get_user_model
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from django.utils.translation import ugettext as _

from Emall.exceptions import UserNotExists
from Emall.response_code import response_code
from manager_app.serializers.auth_serializers import ManagerLoginSerializer, ManagerRegisterSerializer
from manager_app.utils.permission import get_permission
from manager_app.utils.token import generate_payload

jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
User = get_user_model()


class ManagerLoginApiView(GenericAPIView):
    """
    管理员登录
    用户名登录
    """

    serializer_class = ManagerLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.check_manager_login(**serializer.validated_data)
        if user:
            payload = generate_payload(user)
            print(payload)
            token = jwt_encode_handler(payload)  # 生成token
            return Response({
                'token':token
            })
        msg = _('用户不存在或密码不正确')
        raise UserNotExists(msg)

    def get(self, request):
        """再次发送token,获取权限"""
        permissions = get_permission(request)
        serializer = self.get_serializer(instance=permissions, many=True)
        return Response(serializer.data)


class ManagerRegisterApiView(GenericAPIView):
    """
    管理员注册
    用户名注册
    """
    serializer_class = ManagerRegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create_manager()
        return response_code.register_success







