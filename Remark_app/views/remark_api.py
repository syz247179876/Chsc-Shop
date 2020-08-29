# -*- coding: utf-8 -*- 
# @Time : 2020/5/29 14:09 
# @Author : 司云中 
# @File : remark_api.py 
# @Software: PyCharm
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from Remark_app.models.remark_models import Remark
from Remark_app.pagination import RemarkResultsSetPagination
from Remark_app.serializers.UserMarkerSerializerApi import UserMarkerSerializer
from e_mall.loggings import Logging
from rest_framework.response import Response
from e_mall.response_code import response_code


common_logger = Logging.logger('django')

evaluate_logger = Logging.logger('evaluate_')


class RemarkOperation(GenericViewSet):

    permission_classes = [IsAuthenticated]

    serializer_class = UserMarkerSerializer

    pagination_class = RemarkResultsSetPagination

    def get_queryset(self):
        """获取用户所浏览的店铺的评论"""
        commodity_pk = self.kwargs.get('commodity_pk')
        return Remark.remark_.select_related('consumer', 'commodity').filter(commodity__pk=commodity_pk, is_remark=True)

    def get_user_remark(self):
        """获取用户对某商品的评论"""
        commodity_pk = self.kwargs.get('commodity_pk')
        return Remark.remark_.select_related('consumer', 'commodity').filter(consumer=self.request.user,
                                                                             commodity__pk=commodity_pk)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)  # page是个page_size大小的可迭代对象
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['put'], detail=False)
    def update_remark(self, request):
        """更新该用户下购买商品的评论内容，评论状态等"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO 后期利用 gensim 对用户的评论进行分析，符合文明素质用于允许评论
        query_object = self.get_user_remark().filter(is_remark=False)
        if query_object.exists():  # 存在机会为True，每个商品只能评论一次
            query_object.update(is_reward=True, **serializer.validated_data)
            return Response(response_code.remark_success, status.HTTP_200_OK)
        else:
            return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """根据id删除评论"""
        remark_obj = self.get_object()
        is_delete = remark_obj.delete()
        if is_delete:
            return Response(response_code.delete_order_success, status=status.HTTP_200_OK)
        else:
            return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

