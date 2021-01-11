# -*- coding: utf-8 -*-
# @Time  : 2021/1/11 下午5:26
# @Author : 司云中
# @File : information_api.py
# @Software: Pycharm
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Emall.exceptions import UniversalServerError
from Emall.loggings import Logging
from Emall.response_code import response_code
from user_app.serializers.individual_info_serializers import IndividualInfoSerializer

consumer_logger = Logging.logger('consumer_')


class SaveInformation(GenericAPIView):
    """
    保存信息
    修改用户名后需重新登录
    """

    permission_classes = [IsAuthenticated]

    serializer_class = IndividualInfoSerializer

    def get_object(self):
        """返回用户对象"""
        return self.request.user

    def patch(self, request):
        """修改用户名"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.get_object().username = serializer.validated_data.get('username')
            self.get_object().save(update_fields=['username'])
        except Exception as e:
            consumer_logger.error(e)
            raise UniversalServerError()
        else:
            return Response(response_code.user_infor_change_success, status=status.HTTP_200_OK)

    def get(self, request):
        """获取用户详细信息"""
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data)
