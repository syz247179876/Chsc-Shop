# -*- coding: utf-8 -*-
# @Time  : 2020/11/14 下午8:03
# @Author : 司云中
# @File : search_api.py
# @Software: Pycharm
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from Emall.loggings import Logging
from search_app.serailaizers.shop_search_serializers import CommoditySerializer
from search_app.tasks import record_user_search
from search_app.utils.elasticsearch import ElasticSearchOperation
from search_app.utils.pagination import CommodityResultsSetPagination
from shop_app.models.commodity_models import Commodity
from search_app.utils.common import identity

common_logger = Logging.logger('django')


class CommoditySearchOperation(GenericAPIView):
    """ES搜索操作"""

    # 索引库表
    index_models = [Commodity]

    serializer_class = CommoditySerializer

    pagination_class = CommodityResultsSetPagination

    # es操作类
    elastic_class = ElasticSearchOperation

    def get_elastic_class(self):
        return self.elastic_class

    def get_elastic(self, *args, **kwargs):
        """获取elastic类"""
        if getattr(self, 'elastic', None):
            return getattr(self, 'elastic')
        _elastic = self.get_elastic_class()
        setattr(self, 'elastic', _elastic(*args, **kwargs))
        return getattr(self, 'elastic')

    def get_queryset(self):
        elastic = self.get_elastic(request=self.request)
        return elastic.get_queryset()

    def get(self, request):
        """请求关键字商品"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)  # 返回一个list页对象,默认返回第一页的page对象
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        self.send_record_signal(request)  # 异步任务发送信号,记录用户浏览记录
        return Response(serializer.data)

    @identity
    def send_record_signal(self, unique_identity):
        """发送记录历史记录信号"""
        record_user_search.delay(unique_identity, self.request.query_params.copy().get('text'))

