# -*- coding: utf-8 -*-
# @Time  : 2021/2/17 下午10:37
# @Author : 司云中
# @File : seller_commodity_api.py
# @Software: Pycharm
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Emall.base_api import BackendGenericApiView
from Emall.decorator import validate_url_data
from Emall.response_code import response_code, ADD_COMMODITY_PROPERTY, MODIFY_COMMODITY_PROPERTY, \
    DELETE_COMMODITY_PROPERTY, ADD_COMMODITY, MODIFY_COMMODITY
from seller_app.serializers.commodity_serializers import SellerCommoditySerializer, SellerCommodityDeleteSerializer, \
    SkuPropSerializer, SkuPropsDeleteSerializer, FreightSerializer, FreightDeleteSerializer
from seller_app.utils.permission import SellerPermissionValidation


class SellerCommodityApiView(GenericAPIView):
    """商家管理商品操作"""

    serializer_class = SellerCommoditySerializer

    serializer_delete_class = SellerCommodityDeleteSerializer

    permission_classes = [IsAuthenticated, SellerPermissionValidation]

    def post(self, request):
        """商家添加商品"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.add_commodity()
        return Response(response_code.result(ADD_COMMODITY, '添加成功'))

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
        return Response(response_code.result(MODIFY_COMMODITY, '修改成功'))

    def delete(self, request):
        """商家删除商品"""
        serializer = self.serializer_delete_class(data=request.data)
        if self.request.query_params.get('all', None) == 'true':
            self.serializer_delete_class.Meta.model.commodity_.all().delete()
        else:
            serializer.is_valid(raise_exception=True)
            serializer.delete_commodity()
        return


class SkuPropApiView(BackendGenericApiView):
    """商品属性规格和值操作"""

    serializer_class = SkuPropSerializer

    serializer_delete_class = SkuPropsDeleteSerializer

    permission_classes = [IsAuthenticated, SellerPermissionValidation]

    @validate_url_data('sku_props', 'pk', null=True)
    def get(self, request):
        """获取商品属性规格和值单个或多个"""
        return super().get(request)

    def post(self, request):
        """添加商品属性规格和值"""
        super().post(request)
        return Response(response_code.result(ADD_COMMODITY_PROPERTY, "添加成功"))

    @validate_url_data('sku_props', 'pk')
    def put(self, request):
        """修改商品属性规格和值"""
        super().put(request)
        return Response(response_code.result(MODIFY_COMMODITY_PROPERTY, "修改成功"))

    def delete(self, request):
        """删除商品属性规格和值"""
        result_num = super().delete(request)
        return Response(response_code.result(DELETE_COMMODITY_PROPERTY, '删除成功')) \
            if result_num else Response(response_code.result(DELETE_COMMODITY_PROPERTY, '无操作,无效数据'))


class FreightApiView(BackendGenericApiView):
    """运费模板视图类"""

    serializer_class = FreightSerializer

    serializer_delete_class = FreightDeleteSerializer

    permission_classes = [IsAuthenticated, SellerPermissionValidation]

    @validate_url_data('freight', 'pk', null=True)
    def get(self, request):
        """获取单个运费详情或所有运费模板"""
        return super().get(request)

    def post(self, request):
        """增加新的运费模板"""
        super().post(request)
        return Response(response_code.result(ADD_COMMODITY_PROPERTY, "添加成功"))

    @validate_url_data('freight', 'pk')
    def put(self, request):
        """修改已有运费模板"""
        super().put(request)
        return Response(response_code.result(MODIFY_COMMODITY_PROPERTY, "修改成功"))

    def delete(self, request):
        """删除已有运费模板"""
        rows = super().delete(request)
        return Response(response_code.result(DELETE_COMMODITY_PROPERTY, "删除成功")) if rows else Response(
            response_code.result(DELETE_COMMODITY_PROPERTY, '无操作,无效数据'))
