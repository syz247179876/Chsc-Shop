# -*- coding: utf-8 -*-
# @Time  : 2021/2/17 下午10:37
# @Author : 司云中
# @File : seller_commodity_api.py
# @Software: Pycharm
from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from Emall.base_api import BackendGenericApiView
from Emall.decorator import validate_url_data
from Emall.exceptions import SqlServerError
from Emall.response_code import response_code, ADD_COMMODITY_PROPERTY, MODIFY_COMMODITY_PROPERTY, \
    DELETE_COMMODITY_PROPERTY, ADD_COMMODITY, MODIFY_COMMODITY, MODIFY_EFFECTIVE_SKU, DELETE_EFFECTIVE_SKU, \
    CREATE_FREIGHT_ITEM, DELETE_FREIGHT_ITEM, DELETE_COMMODITY
from seller_app.serializers.commodity_serializers import SellerCommoditySerializer, SellerCommodityDeleteSerializer, \
    SkuPropSerializer, SkuPropsDeleteSerializer, FreightSerializer, FreightDeleteSerializer, SellerSkuSerializer, \
    SellerSkuDeleteSerializer, SkuCommoditySerializer, FreightItemSerializer, CommodityCategorySerializer, \
    CommodityFreightSerializer
from seller_app.utils.permission import SellerPermissionValidation
from shop_app.models.commodity_models import Commodity


class SellerCommodityApiView(GenericAPIView):
    """商家管理商品操作"""

    serializer_class = SellerCommoditySerializer

    serializer_delete_class = SellerCommodityDeleteSerializer

    permission_classes = [IsAuthenticated, SellerPermissionValidation]

    def get_queryset(self):
        return Commodity.commodity_.filter(user=self.request.user).annotate(count=Count('id'))

    def post(self, request):
        """商家添加商品"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.add_commodity()
        return Response(response_code.result(ADD_COMMODITY, '添加成功'))

    @validate_url_data('commodity', 'pk', null=True)
    def get(self, request):
        """获取单个商品详情或全部分商品"""
        pk = request.query_params.get('pk', None)
        if pk:
            instance = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(instance=instance)
            return Response(serializer.data)
        else:
            instance = self.get_queryset()
            serializer = self.get_serializer(instance=instance, many=True)
        return Response({
            'count': instance.count(),
            'data': serializer.data
        })

    @validate_url_data('commodity', 'pk')
    def put(self, request):
        """商家修改商品信息"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = serializer.update_commodity()
        return Response(
            response_code.result(MODIFY_COMMODITY, '修改成功') if res else response_code.result(MODIFY_COMMODITY, '无数据改动'))

    def delete(self, request):
        """商家删除商品"""
        serializer = self.serializer_delete_class(data=request.data)
        print(self.request.query_params.get('all', None))
        try:
            if self.request.query_params.get('all', None) == 'true':
                rows = Commodity.commodity_.filter(user=request.user).delete()
            else:
                serializer.is_valid(raise_exception=True)
                rows = serializer.delete_commodity()
        except TypeError:
            raise SqlServerError('商品存在其他关联项，请先删除与商品关联的其他项')
        return Response(response_code.result(DELETE_COMMODITY, '删除成功' if rows else '无效操作'))


class SellerCommodityExtraApiView(GenericViewSet):
    """商家对商品有关的所有额外数据的操作"""

    serializer_category_class = CommodityCategorySerializer

    serializer_freight_class = CommodityFreightSerializer

    def get_category_queryset(self):
        """获取商品所有分类信息"""
        return self.serializer_category_class.Meta.model.objects.filter(has_prev=False).first()

    def get_freight_queryset(self):
        """获取该商家下的所有运费模板信息"""
        return self.serializer_freight_class.Meta.model.objects.filter(user=self.request.user)

    def list(self, request):
        """获取与商品相关的所有额外数据"""
        serializer_category = self.serializer_category_class(instance=self.get_category_queryset())
        serializer_freight = self.serializer_freight_class(instance=self.get_freight_queryset(), many=True)
        return Response({
            'category': serializer_category.data,
            'freight': serializer_freight.data
        })


class SkuPropApiView(BackendGenericApiView):
    """商品属性规格和值操作"""

    serializer_class = SkuPropSerializer

    serializer_delete_class = SkuPropsDeleteSerializer

    serializer_commodity_class = SkuCommoditySerializer

    permission_classes = [IsAuthenticated, SellerPermissionValidation]

    def get_queryset(self):
        """获取该商家所属的商品属性规格和值"""
        return self.serializer_class.Meta.model.objects.select_related('commodity__user'). \
            filter(commodity__user=self.request.user)

    def get_commodity_queryset(self):
        """获取该商家所属下的商品数据"""
        return self.serializer_commodity_class.Meta.model.commodity_.filter(user=self.request.user). \
            values('pk', 'commodity_name')

    @validate_url_data('sku_props', 'pk', null=True)
    def get(self, request):
        """获取商品属性规格和值单个或多个"""
        response = super().get(request)
        commodity_queryset = self.get_commodity_queryset()
        commodity_serializer = self.serializer_commodity_class(instance=commodity_queryset, many=True)
        response.data.update({'commodity': commodity_serializer.data})
        return response

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

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(user=self.request.user).prefetch_related('freight_items')

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
        return Response(response_code.result(DELETE_COMMODITY_PROPERTY, "删除成功" if rows else '无操作,无效数据'))


class FreightItemApiView(GenericViewSet):
    """运费模板项相关API"""

    permission_classes = [IsAuthenticated, SellerPermissionValidation]

    serializer_class = FreightItemSerializer

    def create(self, request):
        """创建运费模板项"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.add()
        return Response(response_code.result(CREATE_FREIGHT_ITEM, '创建成功', data={'pk': obj.pk}))

    def destroy(self, request, pk):
        """删除运费模板项"""
        rows, _ = self.serializer_class.Meta.model.objects.filter(pk=pk).delete()
        return Response(response_code.result(DELETE_FREIGHT_ITEM, '删除成功' if rows else '无效操作'))


class SellerSkuApiView(BackendGenericApiView):
    """商家管理某商品的有效SKU集合"""

    serializer_class = SellerSkuSerializer

    serializer_delete_class = SellerSkuDeleteSerializer

    serializer_commodity_class = SkuCommoditySerializer

    permission_classes = [IsAuthenticated, SellerPermissionValidation]

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.select_related('commodity__user'). \
            filter(commodity__user=self.request.user)

    def get_commodity_queryset(self):
        """获取该商家所属下的商品数据"""
        return self.serializer_commodity_class.Meta.model.commodity_.filter(user=self.request.user). \
            values('pk', 'commodity_name')

    @validate_url_data('sku', 'pk', null=True)
    def get(self, request):
        """获取单个/多个有效SKU"""
        response = super().get(request)
        commodity_queryset = self.get_commodity_queryset()
        commodity_serializer = self.serializer_commodity_class(instance=commodity_queryset, many=True)
        response.data.update({'commodity': commodity_serializer.data})
        return response

    @validate_url_data('sku', 'pk')
    def put(self, request):
        """修改有效SKU"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rows = serializer.modify()
        return Response(response_code.result(MODIFY_EFFECTIVE_SKU, '修改成功' if rows else '无操作，无效数据'))

    def post(self, request):
        """添加新的有效SKU"""
        super().post(request)
        return Response(response_code.result(MODIFY_EFFECTIVE_SKU, '添加成功'))

    def delete(self, request):
        """删除单个/全部SKU"""
        rows = super().delete(request)
        return Response(response_code.result(DELETE_EFFECTIVE_SKU, '删除成功' if rows else '无操作,无效数据'))
