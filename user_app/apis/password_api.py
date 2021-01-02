# -*- coding: utf-8 -*-
# @Time  : 2021/1/1 下午7:33
# @Author : 司云中
# @File : password_api.py
# @Software: Pycharm


from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from Emall.exceptions import NoBindPhone
from Emall.response_code import response_code
from universal_app.redis.retrieve_password_redis import RetrievePasswordRedis
from user_app.redis.user_redis import RedisUserOperation
from user_app.serializers.password_serializers import PasswordSerializer
from user_app.serializers.retrieve_password_serializers import RetrievePasswordSerializer, NewPasswordSerializer
from Emall.base_redis import BaseRedis


class RetrievePasswordOperation(GenericAPIView):
    """找回密码"""

    serializer_class = RetrievePasswordSerializer
    redis_manager = BaseRedis.choice_redis_db('redis')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'redis_manager': self.redis_manager})
        return context

    def post(self, request):
        """
        找回密码(1)：
        1.输入手机号/邮箱
        2.获取手机号/邮箱验证码
        3.验证手机号/邮箱和验证码是否吻合,如果吻合,需要生成修改唯一密码凭证,确保当前手机号/邮箱与之前的手机号/邮箱一致(可以前端传客户端mac)

        (验证通过，无回复内容进入重置密码界面）
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request):
        """
        找回密码(2):

        1.解析请求体,获取组合唯一凭证
        2.校验唯一凭证
        3.修改密码
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        serializer.renew_password(serializer.validated_data)
        return Response(response_code.modify_password)


class NewPassword(GenericAPIView):
    """更换新密码"""

    serializer_class = NewPasswordSerializer
    redis = RetrievePasswordRedis.choice_redis_db('redis')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'redis': self.redis})
        return context

    def post(self, request):
        """
        找回密码(2)
        1.验证唯一凭证和密码是否和之前的密码一致
        2.修改密码
        3.返回修改结果,删除唯一凭证
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_updated = serializer.update_password(serializer.validated_data)
        if is_updated:
            return Response(serializer.validated_data.pop('identity'))
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePassword(GenericAPIView):
    """
    修改当前用户的密码
    """

    permission_classes = [IsAuthenticated]

    serializer_class = PasswordSerializer

    redis = RedisUserOperation.choice_redis_db('redis')

    def get_object(self):
        """返回用户对象"""
        return self.request.user

    @property
    def get_object_phone(self):
        """获取用户名"""
        if self.request.user.get_phone == '':
            raise NoBindPhone()  # 用户绑定手机号
        return self.request.user.get_phone

    def modify_password(self, user, validated_data):
        """改变用户的密码"""

        old_password = validated_data.get('old_password')
        new_password = validated_data.get('new_password')
        code = validated_data.get('code')
        is_code_checked = self.redis.check_code(self.get_object_phone, code)
        is_checked = user.check_password(old_password)  # 核查旧密码
        if not is_code_checked:
            # 验证码不正确
            return Response(response_code.verification_code_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif not is_checked:
            # 旧密码不正确
            return Response(response_code.user_original_password_error,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            user.set_password(new_password)  # 设置新密码
            try:
                user.save(update_fields=["password"])
            except Exception:
                return Response(response_code.modify_password_verification_error,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(response_code.modify_password_verification_success, status=status.HTTP_200_OK)

    def patch(self, request):
        """处理用户密码"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.modify_password(self.get_object(), serializer.validated_data)
