# -*- coding: utf-8 -*-
# @Time  : 2021/2/17 下午10:37
# @Author : 司云中
# @File : seller_commodity_api.py
# @Software: Pycharm
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from Emall.decorator import validate_url_data
from seller_app.serializers.commodity_serializers import SellerCommoditySerializer, SellerCommodityDeleteSerializer


class ManageCommodityApiView(GenericAPIView):
    """商家管理商品操作"""

    serializer_class = SellerCommoditySerializer

    serializer_delete_class = SellerCommodityDeleteSerializer

    def post(self, request):
        """商家添加商品"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.add_commodity()
        return

    @validate_url_data('commodity', 'pk', null=True)
    def get(self, request):
        """获取单个分组详情或全部分组记录"""
        pk = request.query_params.get('pk', None)
        if request.query_params.get('pk', None):
            instance = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(instance=instance)
        else:
            instance = self.get_queryset()
            serializer = self.get_serializer(instance=instance, many=True)
        return Response(serializer.data)

    def put(self, request):
        """商家修改商品信息"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        serializer.update_commodity()
        return

    def delete(self, request):
        """商家删除商品"""
        serializer = self.serializer_delete_class(data=request.data)
        if self.request.query_params.get('all', None) == 'true':
            self.serializer_delete_class.Meta.model.commodity_.all().delete()
        else:
            serializer.is_valid(raise_exception=True)
            serializer.delete_commodity()
        return
