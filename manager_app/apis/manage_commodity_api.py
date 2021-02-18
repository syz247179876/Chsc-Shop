# -*- coding: utf-8 -*-
# @Time  : 2021/2/9 下午10:52
# @Author : 司云中
# @File : manage_commodity_api.py
# @Software: Pycharm

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from Emall.decorator import validate_url_data
from Emall.response_code import response_code, ADD_COMMODITY_CATEGORY, DELETE_COMMODITY_CATEGORY, \
    MODIFY_COMMODITY_CATEGORY, ADD_COMMODITY_GROUP, DELETE_COMMODITY_GROUP, MODIFY_COMMODITY_GROUP
from manager_app.serializers.commodity_serializers import CommodityCategoryCreateSerializer, \
    CommodityCategoryDeleteSerializer, CommodityCategorySerializer, CommodityGroupDeleteSerializer, \
    CommodityGroupSerializer
from shop_app.models.commodity_models import CommodityCategory, CommodityGroup


class ManagerCommodityCategoryApiView(GenericAPIView):
    """商家管理商品分类操作API"""
    serializer_create_class = CommodityCategoryCreateSerializer

    serializer_delete_class = CommodityCategoryDeleteSerializer

    serializer_class = CommodityCategorySerializer

    def get_queryset(self):
        return CommodityCategory.objects.all()

    def post(self, request):
        """添加类别"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create_category()
        return Response(response_code.result(ADD_COMMODITY_CATEGORY, '添加成功'))

    def delete(self, request):
        """删除类别"""
        serializer = self.serializer_delete_class(data=request.data)
        if self.request.query_params.get('all', None) == 'true':
            self.serializer_class.Meta.model.objects.all().delete()
        else:
            serializer.is_valid(raise_exception=True)
            CommodityCategory.objects.filter(pk__in=serializer.validated_data.get('pk_list')).delete()
        return Response(response_code.result(DELETE_COMMODITY_CATEGORY, '删除成功'))

    def put(self, request):
        """修改类别"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update_category()
        return Response(response_code.result(MODIFY_COMMODITY_CATEGORY, '修改成功'))

    @validate_url_data('category', 'pk', null=True)
    def get(self, request):
        """获取单个类别详情 或 全部类别记录"""
        pk = request.query_params.get('pk', None)
        if pk:
            instance = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(instance=instance)
        else:
            instance = self.get_queryset()
            serializer = self.get_serializer(instance=instance, many=True)
        return Response(serializer.data)


class ManageCommodityGroupApiView(GenericAPIView):
    """管理商品分组操作API"""

    serializer_delete_class = CommodityGroupDeleteSerializer

    serializer_class = CommodityGroupSerializer

    def get_queryset(self):
        return CommodityGroup.commodity_group_.all()

    @validate_url_data('commodity_group', 'pk', null=True)
    def get(self, request):
        """获取单个分组详情或全部分组记录"""
        pk = request.query_params.get('pk', None)
        if pk:
            instance = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(instance=instance)
        else:
            instance = self.get_queryset()
            serializer = self.get_serializer(instance=instance, many=True)
        return Response(serializer.data)


    def post(self, request):
        """添加分组记录"""
        serializer = self.get_serializer(datat=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.add_group()
        return Response(response_code.result(ADD_COMMODITY_GROUP, '添加成功'))

    def delete(self, request):
        """删除分组记录"""
        serializer = self.serializer_delete_class(data=request.data)
        if request.query_params.get('all', None) == 'true':
            self.get_queryset().delete()
        else:
            serializer.is_valid(raise_exception=True)
            CommodityCategory.objects.filter(pk__in=serializer.validated_data.get('pk_list')).delete()
        return Response(response_code.result(DELETE_COMMODITY_GROUP, '删除成功'))

    @validate_url_data('commodity_group', 'pk')
    def put(self, request):
        """修改分组"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update_group()
        return Response(response_code.result(MODIFY_COMMODITY_GROUP, '修改成功'))


