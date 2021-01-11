# -*- coding: utf-8 -*-
# @Time  : 2021/1/11 下午5:51
# @Author : 司云中
# @File : history_api.py
# @Software: Pycharm
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from Emall.exceptions import DataFormatError
from Emall.response_code import response_code
from search_app import signals
from search_app.utils.common import identity


class HistoryOperation(GenericAPIView):

    def delete(self, request):
        """单删历史搜索记录"""
        if request.query_params.get('many') == 'true':
            result = self.send_delete_signal(request, many=True)
        else:
            if not request.query_params.get('key', None):
                raise DataFormatError()
            result = self.send_delete_signal(request)
        return Response(result, status=status.HTTP_200_OK)

    @identity
    def send_delete_signal(self, request, unique_identity=None, many=False):
        """
        发送删除历史搜索记录信号
        发个信号玩玩
        """

        if many:
            result = signals.del_search_all.send(sender=unique_identity, request=request)
        else:
            result = signals.del_search_single.send(sender=unique_identity, request=request,
                                                    key=request.query_params.get('key', ''))
        return response_code.delete_history_success if result[0][1] else {"Do Nothing"}


    @identity
    def get(self, request, unique_identity=None, **kwargs):
        """获取用户的搜索记录"""
        page = self.request.query_params.get('page', 1)
        limit = self.request.query_params.get('limit', 10)
        result = signals.retrieve_record.send(sender=unique_identity, request=request, **kwargs)[0][1]  # 获取回调函数的结果
        return Response({'page': page, 'limit': limit, 'data': result})

