# -*- coding: utf-8 -*-
# @Time  : 2020/10/13 下午7:41
# @Author : 司云中
# @File : retrieve_pwd_api.py
# @Software: Pycharm
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from CommonModule_app.serailizers.retrieve_password_serializers import RetrievePasswordSerializer
from e_mall.base_redis import BaseRedis


class RetrievePasswordOperation(GenericViewSet):

    serializer_class = RetrievePasswordSerializer
    redis = BaseRedis.choice_redis_db('redis')


    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'redis':self.redis})

    def post(self, request):
        """
        找回密码第一步：
        1.验证邮箱/手机
        (验证通过，无回复内容进入重置密码界面）
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request):
        """
        找回密码第二步：
        2.重置密码，更换新密码
        """
        pass





