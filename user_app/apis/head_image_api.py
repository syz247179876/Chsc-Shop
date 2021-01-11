# -*- coding: utf-8 -*-
# @Time  : 2021/1/11 下午5:24
# @Author : 司云中
# @File : head_image_api.py
# @Software: Pycharm
import importlib

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Emall.exceptions import OSSError, UserNotExists
from Emall.response_code import response_code
from user_app.serializers.individual_info_serializers import HeadImageSerializer

User = get_user_model()


class HeadImageOperation(GenericAPIView):
    """
    修改头像
    """
    permission_classes = [IsAuthenticated]

    serializer_class = HeadImageSerializer

    storage_class = settings.DEFAULT_FILE_STORAGE

    def get_storage_class(self):
        return self.storage_class

    def get_storage(self, **kwargs):
        """
        动态导入模块，生成storage实例对象
        :param kwargs:
        :return: instance
        """
        module_path, class_name = self.get_storage_class().rsplit('.', 1)
        storage = getattr(importlib.import_module(module_path), class_name)
        return storage(**kwargs)

    def get_object(self):
        """
        获取消费者对象
        :return: instance
        """
        try:
            return self.request.user
        except User.DoesNotExist:
            raise UserNotExists()

    def put(self, request):
        """修改头像"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_modify = serializer.update_head_image(self.get_object(), serializer.validated_data, self.get_storage())
        if is_modify:
            return Response(response_code.modify_head_image_success, status=status.HTTP_200_OK)
        raise OSSError()  # FastDFS 或者 第三方服务错误
