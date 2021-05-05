# -*- coding: utf-8 -*-
# @Time  : 2021/2/18 下午4:17
# @Author : 司云中
# @File : seller_store_api.py
# @Software: Pycharm
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Emall.exceptions import DataNotExist
from Emall.response_code import response_code, CREATE_STORE
from seller_app.serializers.store_serializers import SellerStoreSerializer, SellerDisplaySerializer

User = get_user_model()
class SellerStoreApiView(GenericAPIView):
    """商家店铺操作API"""

    serializer_class = SellerStoreSerializer

    serializer_display_class = SellerDisplaySerializer

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """创建店铺"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.create_store()
        return Response(response_code.result(CREATE_STORE, '创建成功'))

    def put(self, request):
        """验证店铺名是否存在"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # 校验店铺名是否唯一
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        """获取店铺数据集"""
        return self.serializer_display_class.Meta.model.objects.select_related('user', 'store', 'role').\
            filter(user=self.request.user, user__is_seller=True)

    def get(self, request, *args, **kwargs):
        """商家获取店铺信息"""
        queryset = self.get_queryset()
        if not queryset.exists():
            raise DataNotExist()
        serializer = self.serializer_display_class(instance=queryset.first())
        return Response(serializer.data)




