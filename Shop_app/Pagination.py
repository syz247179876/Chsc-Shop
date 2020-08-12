# -*- coding: utf-8 -*-
# @Time  : 2020/8/12 下午7:55
# @Author : 司云中
# @File : Pagination_class.py
# @Software: Pycharm
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CommodityResultsSetPagination(PageNumberPagination):
    page_size = 10  # 每页大小
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100  # 总页数

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
