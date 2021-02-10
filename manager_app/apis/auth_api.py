# -*- coding: utf-8 -*-
# @Time  : 2021/2/9 下午10:44
# @Author : 司云中
# @File : auth_api.py
# @Software: Pycharm
from django.contrib.auth import get_user_model
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from Emall.exceptions import UserNotExists
from manager_app.serializers.auth_serializers import ManagerLoginSerializer

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
            token = jwt_encode_handler(payload)  # 生成token
            return Response({
                'token':token
            })
        msg = _('用户不存在或密码不正确')
        raise UserNotExists(msg)

class ManagerRegisterApiView(GenericAPIView):
    """
    管理员注册
    用户名注册
    """
    pass


class ManagerRoleApiView(GenericAPIView):
    """
    根据token解析role,获取目标用户所属角色的权限
    """

    def get(self, head):

