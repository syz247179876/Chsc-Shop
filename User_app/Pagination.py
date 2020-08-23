# -*- coding: utf-8 -*-
# @Time  : 2020/8/18 下午11:01
# @Author : 司云中
# @File : Pagination.py
# @Software: Pycharm

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class FootResultsSetPagination(PageNumberPagination):
    page_size = 20  # 每页大小
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 5  # 总页数

    def get_paginated_response(self, data):
        """
        重写封装返回给前端的数据
        设置分页格式
        """
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'data': data
        })

class FavoritesPagination(PageNumberPagination):
    page_size = 10  # 每页大小
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 50 # 总页数50

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'data': data
        })

class TrolleyResultsSetPagination(PageNumberPagination):
    page_size = 5  # 每页大小
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100  # 总页数100页

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'data': data
        })