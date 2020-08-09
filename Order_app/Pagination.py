# -*- coding: utf-8 -*-
# @Time  : 2020/8/9 下午8:28
# @Author : 司云中
# @File : Pagination.py
# @Software: Pycharm
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class OrderResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 10000

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
            'count': self.page.paginator.count,  # 当前页数的数量
            'data': data
        })
