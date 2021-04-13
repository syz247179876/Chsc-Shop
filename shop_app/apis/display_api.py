# -*- coding: utf-8 -*-
# @Time  : 2021/4/13 下午2:19
# @Author : 司云中
# @File : display_api.py
# @Software: Pycharm
import json

from django.conf import settings
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from Emall.exceptions import DataFormatError
from search_app.signals import retrieve_from_es, parse_hits
from shop_app.models.commodity_models import Commodity
from shop_app.serializers.diplay_serializers import CommodityDisplaySerializer


class CommodityDisplay(GenericViewSet):
    """用于商品的显示API"""

    serializer_class = CommodityDisplaySerializer

    def dsl_body(self, q):
        """
        DSL表达式的body部分
        使用bool表达式将多个叶子语句合并成单一语句进行查找
        """
        return {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"commodity_name": q}},
                        {"match": {"intro": q}},
                        {"match": {"category": q}}
                    ]
                }
            }
        }

    def retrieve_dsl(self, index=None, **kwargs):
        """
        获取商品的dsl表达式
        :param index: 索引库名，可自定义/从配置文件读
        :param kwargs: 其他body参数
        :return:
        """
        return {
            "sender": index or settings.ES_INDICES.get('default'),
            "body": kwargs
        }

    def get_keyword_queryset(self, pk_list):
        """按照pk_list进行查询，然后按照指定的顺序排序"""
        ordering = 'FIELD(`id`, {})'.format(','.join([str(pk) for pk in pk_list]))  # 设定排序
        return Commodity.commodity_.filter(pk__in=pk_list).extra(select={"ordering": ordering},
                                                                 order_by=("ordering",))

    @action(detail=False, methods=['GET'], url_path='keyword')
    def keyword_list(self, request):
        """关键字搜索，获取商品API"""
        if not request.query_params.get('q', None):
            raise DataFormatError('缺少必要参数')
        keyword = request.query_params.get('q')
        results = retrieve_from_es.send(**self.retrieve_dsl(**self.dsl_body(keyword)))[0]
        code, res = results[1]
        if code == 200:
            pk_list = parse_hits.send(sender=self.__class__.__name__, result=res)[0]
            serializer = self.get_serializer(instance=self.get_keyword_queryset(list(pk_list[1])), many=True)
            return Response(serializer.data)
        return Response([])
