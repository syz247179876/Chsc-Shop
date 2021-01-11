# -*- coding: utf-8 -*-
# @Time  : 2021/1/11 下午7:21
# @Author : 司云中
# @File : heat_api.py
# @Software: Pycharm
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from Emall.response_code import response_code
from search_app import signals


class HeatSearchOperation(GenericAPIView):
    """热度搜索操作"""

    def get(self, request):
        """获取当天搜索热度关键字"""
        response_code.retrieve_heat_search.update({'data': signals.retrieve_heat_keyword.send(sender=self)[0][1]})
        return Response(response_code.retrieve_heat_search)
