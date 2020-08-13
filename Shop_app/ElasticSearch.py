# -*- coding: utf-8 -*-
# @Time  : 2020/8/12 上午8:10
# @Author : 司云中
# @File : sadas sa.py
# @Software: Pycharm

import requests
from django.urls import reverse
import requests

from Shop_app.models.commodity_models import Commodity
from e_mall.loggings import Logging

common_logger = Logging.logger('django')


class ElasticSearchOperation:
    """直接对es的请求封装"""

    # __slots__ = ('query', '_instance', 'url', 'request')
    Model = Commodity

    BASE_URL = 'http://192.168.0.105:9200/'
    FUNC = '_search'
    INDEX_DB = 'shop'

    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(cls, '_instance'):
    #         cls._instance = super().__new__(cls, *args, **kwargs)
    #     return cls._instance

    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def combine_url(self):
        assert hasattr(self, 'request'), 'Should include request '
        if hasattr(self, 'url'):
            return self.url
        query = self.request.query_params.copy()
        query.pop('page')
        url = self.BASE_URL + self.INDEX_DB + '/' + self.FUNC + '?' + '&'.join(
            ['q=' + key + ':' + value for key, value in query.items()])
        setattr(self, 'url', url)
        common_logger.info(url)
        return url

    def get_search_results(self):
        if hasattr(self, 'pk_list'):
            return self.pk_list
        url = self.combine_url()
        response = requests.get(url).json()
        hits = response.get('hits').get('hits')
        pk_list = [int(document.get('_source').get('django_id')) for document in hits]
        setattr(self, 'pk_list', pk_list)
        common_logger.info(pk_list)
        return pk_list

    def get_queryset(self):
        """根据索引结果查询数据库"""
        assert hasattr(self, 'Model'), 'Should define Model'
        pk_list = self.get_search_results()
        ordering = 'FIELD(`id`, {})'.format(','.join([str(pk) for pk in pk_list]))  # 设定排序
        return self.Model.commodity_.filter(pk__in=pk_list).extra(select={"ordering": ordering}, order_by=("ordering",))
