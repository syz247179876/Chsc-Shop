# -*- coding: utf-8 -*-
# @Time  : 2021/1/11 下午5:07
# @Author : 司云中
# @File : ocr_api.py
# @Software: Pycharm
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Emall.response_code import response_code
from user_app.serializers.individual_info_serializers import VerifyIdCardSerializer


class VerifyIdCard(GenericAPIView):
    """
    OCR身份识别验证
    """

    permission_classes = [IsAuthenticated]

    serializer_class = VerifyIdCardSerializer

    def get_object(self):
        """获取inner join的用户对象"""
        return self.request.user  # 如果没有对象在权限会那抛出404

    def put(self, request):
        """处理POST请求"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(self.get_object(), serializer.validated_data)
        return Response(response_code.verify_id_card_success, status=status.HTTP_200_OK)