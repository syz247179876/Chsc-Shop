# -*- coding: utf-8 -*-
# @Time  : 2020/11/14 下午8:03
# @Author : 司云中
# @File : search_api.py
# @Software: Pycharm
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from Emall.loggings import Logging
from search_app import signals
from search_app.serailaizers.shop_search_serializers import CommoditySerializer
from shop_app.models.commodity_models import Commodity
from search_app.utils.elasticsearch import ElasticSearchOperation
from search_app.utils.pagination import CommodityResultsSetPagination
from rest_framework.viewsets import GenericViewSet

common_logger = Logging.logger('django')

def is_login(func):
    """判断是否登录装饰器"""

    def decorate(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            identity = request.user.pk
        else:
            identity = None
        func(self, request, identity, *args, **kwargs)

    return decorate

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
        if getattr(self, 'elastic', None):
            return getattr(self, 'elastic')
        elastic_ = self.get_elastic_class()
        setattr(self, 'elastic', elastic_(*args, **kwargs))
        return getattr(self, 'elastic')

    def get_queryset(self):
        elastic = self.get_elastic(request=self.request)
        return elastic.get_queryset()

    def post(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)  # 返回一个list页对象,默认返回第一页的page对象
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        self.send_record_signal(request)  # 发送消息,记录用户浏览记录
        return Response(serializer.data)

    def get(self, request):
        """test"""
        self.send_record_signal(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


    def delete(self, request):
        """单删"""
        if request.GET.get('many') == 'true':
            print(2222)
            self.send_delete_signal(request, many=True)
        else:
            self.send_delete_signal(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @is_login
    def send_delete_signal(self, request, identity=None, many=False):
        """发送删除历史搜索记录信号"""
        if many:
            signals.del_search_all.send(sender=identity, request=request)
        else:
            signals.del_search_single.send(sender=identity, request=request, key=request.GET.get('text',''))


    @is_login
    def send_record_signal(self, request, identity=None):
        """发送记录历史记录信号"""
        query = self.request.query_params.copy()
        signals.record_search.send(sender=identity, request=request, key=query.get('text'))

    # pagination_class = CommodityResultsSetPagination

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     page = self.paginate_queryset(queryset)  # 返回一个list页对象,默认返回第一页的page对象
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

