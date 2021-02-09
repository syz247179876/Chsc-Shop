# -*- coding: utf-8 -*-
# @Time  : 2021/1/11 下午5:33
# @Author : 司云中
# @File : cart_api.py
# @Software: Pycharm
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from Emall.response_code import response_code
from user_app.model.trolley_models import Trolley
from user_app.redis.shopcart_redis import shopcart
from user_app.serializers.shopcart_serializers import ShopCartSerializer
from user_app.utils.pagination import TrolleyResultsSetPagination


class ShopCartOperation(GenericViewSet):
    """购物车的相关操作"""

    model_class = Trolley

    permission_classes = [IsAuthenticated]

    redis = shopcart

    serializer_class = ShopCartSerializer  # 序列化器

    pagination_class = TrolleyResultsSetPagination

    def get_model_class(self):
        return self.model_class

    def get_queryset(self):
        return self.get_model_class().trolley_.select_related('commodity', 'store').filter(user=self.request.user)

    def get_delete_queryset(self, pk_list):
        return self.get_model_class().trolley_.filter(user=self.request.user, pk__in=pk_list)

    def list(self, request):
        """显示购物车列表"""

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request):
        """单删购物车中的商品"""
        obj = self.get_object()
        row_counts, delete_dict = obj.delete()
        if row_counts:
            return Response(response_code.delete_shop_cart_good_success)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['delete'], detail=False)
    def destroy_many(self, request):
        """群删购物车中的商品"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        queryset = self.get_delete_queryset(serializer.validated_data.get('pk_list'))
        row_counts, delete_dict = queryset.delete()
        if row_counts:
            return Response(response_code.delete_shop_cart_good_success)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request):
        """添加商品到购物车"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        is_created = serializer.add_trolley(serializer.validated_data)
        if is_created:
            return Response(response_code.add_goods_into_shop_cart_success)
        return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
