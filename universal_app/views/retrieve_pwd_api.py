# -*- coding: utf-8 -*-
# @Time  : 2020/10/13 下午7:41
# @Author : 司云中
# @File : retrieve_pwd_api.py
# @Software: Pycharm
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from universal_app.redis.retrieve_password_redis import RetrievePasswordRedis
from universal_app.serailizers.retrieve_password_serializers import RetrievePasswordSerializer, NewPasswordSerializer
from Emall.base_redis import BaseRedis
import uuid


class RetrievePasswordOperation(GenericViewSet):

    serializer_class = RetrievePasswordSerializer
    redis = BaseRedis.choice_redis_db('redis')


    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'redis':self.redis})

    def post(self, request):
        """
        找回密码(1)：
        1.收入手机号/邮箱
        2.获取手机号/邮箱验证码
        3.验证手机号/邮箱和验证码是否吻合,如果吻合,需要生成修改唯一密码凭证,确保当前手机号/邮箱与之前的手机号/邮箱一致(可以前端传客户端mac)

        (验证通过，无回复内容进入重置密码界面）
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NewPassword(GenericViewSet):
    """更换新密码"""

    serializer_class = NewPasswordSerializer
    redis = RetrievePasswordRedis.choice_redis_db('redis')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'redis': self.redis})


    def post(self, request):
        """
        找回密码(2)
        1.验证唯一凭证和密码是否和之前的密码一致
        2.修改密码
        3.返回修改结果,删除唯一凭证
        """

        serializer = self.get_serializer(request.data)
        serializer.is_valid(raise_exception=True)
        is_updated = serializer.update_password(serializer.validated_data)
        if is_updated:
            return Response(serializer.validated_data.pop('identity'))
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


