# -*- coding: utf-8 -*-
# @Time  : 2021/5/31 下午4:02
# @Author : 司云中
# @File : common_api.py
# @Software: Pycharm
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.conf import settings

class SettingsApiView(GenericViewSet):
    """提供配置信息"""

    permission_classes = [IsAuthenticated]

    @action(methods=['GET'], url_path='oss', detail=False)
    def supply_oss(self, request):
        """提供oss相关配置"""
        return Response({
            'region':settings.OSS_REGION,
            'accessKeyId': settings.OSS_ACCESS_KEY_ID,
            'accessKeySecret': settings.OSS_ACCESS_KEY_SECRET,
            'bucket': settings.OSS_BUCKET
        })