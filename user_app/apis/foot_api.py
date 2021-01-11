# -*- coding: utf-8 -*-
# @Time  : 2021/1/11 下午5:32
# @Author : 司云中
# @File : foot_api.py
# @Software: Pycharm
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from Emall.decorator import validate_url_data
from Emall.exceptions import UniversalServerError
from shop_app.models.commodity_models import Commodity
from user_app.redis.foot_redis import FootRedisOperation
from user_app.serializers.foot_serializers import FootSerializer
from user_app.utils.pagination import FootResultsSetPagination


class FootOperation(GenericViewSet):
    """浏览足迹处理"""

    permission_classes = [IsAuthenticated]

    redis = FootRedisOperation.choice_redis_db('redis')

    pagination_class = FootResultsSetPagination

    serializer_class = FootSerializer  # 序列化器

    def get_serializer_context(self):
        return {
            'timestamp': self.get_commodity_dict
        }

    @property
    def get_commodity_dict(self):
        """缓存{commodity_pk:timestamp}"""
        return self.commodity_dict if hasattr(self, 'commodity_dict') else {}

    def get_queryset(self):
        """获取足迹固定数量的商品查询集"""
        page_size = FootResultsSetPagination.page_size
        page = self.request.query_params.get(self.pagination_class.page_query_param, 1)  # 默认使用第一页
        # 按照固定顺序查询固定范围内的商品pk列表
        commodity_dict = self.redis.get_foot_commodity_id_and_page(self.request.user.pk, page=page, page_size=page_size)
        print(commodity_dict)
        setattr(self, 'commodity_dict', commodity_dict)
        ordering = 'FIELD(`id`,{})'.format(','.join((str(pk) for pk in commodity_dict.keys())))
        return Commodity.commodity_.filter(pk__in=commodity_dict.keys()).extra(select={"ordering": ordering},
                                                                               order_by=(
                                                                                   "ordering",)) if commodity_dict else []

    def create(self, request):
        """单增用户足迹"""
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.redis.add_foot_commodity_id(user.pk, serializer.validated_data)
        return Response({"OK"}, status=status.HTTP_204_NO_CONTENT)

    # @method_decorator(cache_page(30, cache='redis'))
    def list(self, request):
        """
        处理某用户固定数量的足迹
        """
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            consumer_logger.error(e)
            raise UniversalServerError()

    @validate_url_data('commodity', 'pk')
    def destroy(self, request, **kwargs):
        """删除一条记录"""
        user = request.user
        pk = kwargs.get('pk')
        self.redis.delete_foot_commodity_id(user.pk, commodity_id=pk)
        return Response({"OK"}, status=status.HTTP_204_NO_CONTENT)  # 删完前端刷新就行了

    @action(methods=['delete'], detail=False)
    def destroy_all(self, request):
        """删除全部记录"""
        user = request.user
        self.redis.delete_foot_commodity_id(user.pk, is_all=True)
        return Response({"OK"}, status=status.HTTP_204_NO_CONTENT)