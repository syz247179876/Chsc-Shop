# -*- coding: utf-8 -*-
# @Time  : 2021/2/18 下午4:17
# @Author : 司云中
# @File : seller_store_api.py
# @Software: Pycharm
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Emall.exceptions import DataNotExist
from Emall.response_code import response_code, CREATE_STORE, USER_INFOR_CHANGE_SUCCESS, MODIFY_SELLER_STORE
from seller_app.serializers.store_serializers import SellerStoreSerializer, SellerDisplaySerializer, \
    SellerUpdateInfoSerializer, SellerUpdateStoreSerializer

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


class SellerInfoApiView(GenericViewSet):
    """
    商家相关信息序列化器
    个人信息，店铺信息，角色信息
    """
    serializer_info_class = SellerUpdateInfoSerializer

    serializer_store_class = SellerUpdateStoreSerializer


    def get_into_serializer(self, *args, **kwargs):
        serializer_class = self.serializer_info_class
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_store_serializer(self, *args, **kwargs):
        serializer_class = self.serializer_store_class
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


    @action(methods=['PUT'], detail=False, url_path='personal')
    def update_seller_info(self, request):
        """更新商家个人信息"""
        serializer = self.get_into_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.modify()
        return Response(response_code.result(USER_INFOR_CHANGE_SUCCESS, '更新成功'))

    @action(methods=['PUT'], detail=False, url_path='store')
    def update_seller_store(self, request):
        """更新商家店铺信息"""
        serializer = self.get_store_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rows = serializer.modify()
        return Response(response_code.result(MODIFY_SELLER_STORE, '更新成功' if rows else '无数据变化'))

