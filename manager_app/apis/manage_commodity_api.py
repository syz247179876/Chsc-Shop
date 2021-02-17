# -*- coding: utf-8 -*-
# @Time  : 2021/2/9 下午10:52
# @Author : 司云中
# @File : manage_commodity_api.py
# @Software: Pycharm

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from Emall.decorator import validate_url_data
from Emall.response_code import response_code
from manager_app.serializers.commodity_serializers import SellerCommoditySerializer, CommodityCategoryCreateSerializer, \
    CommodityCategoryDeleteSerializer, CommodityCategorySerializer
from shop_app.models.commodity_models import CommodityCategory


class ManageCommodityApiView(GenericAPIView):
    """商家管理商品操作"""

    serializer_class = SellerCommoditySerializer


class ManagerCommodityCategoryApiView(GenericAPIView):
    """商家管理商品分类操作"""
    serializer_create_class = CommodityCategoryCreateSerializer

    serializer_delete_class = CommodityCategoryDeleteSerializer

    serializer_class = CommodityCategorySerializer

    def get_queryset(self):
        return CommodityCategory.commodity_category_.all()

    def post(self, request):
        """添加类别"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create_category()
        return response_code.add_commodity_category

    def delete(self, request):
        """删除类别"""
        serializer = self.serializer_delete_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        CommodityCategory.commodity_category_.filter(pk__in=serializer.validated_data.get('pk_list')).delete()
        return

    def put(self, request):
        """修改类别"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update_category()

    @validate_url_data('category', 'pk', null=True)
    def get(self, request):
        """获取详细类别 或 全部类别记录"""
        pk = request.query_params.get('pk', None)
        if pk:
            instance = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(instance=instance)
        else:
            instance = self.get_queryset()
            serializer = self.get_serializer(instance=instance, many=True)
        return Response(serializer.data)
