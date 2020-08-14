# -*- coding: utf-8 -*- 
# @Time : 2020/5/29 14:09 
# @Author : 司云中 
# @File : remark_api.py 
# @Software: PyCharm
from rest_framework import status
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.mixins import ListModelMixin
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
    serializer_class = UserMarkerSerializer

    pagination_class = RemarkResultsSetPagination

    def get_queryset(self):
        """获取用户所浏览的店铺的评论"""
        commodity_pk = self.kwargs.get('commodity_pk')
        return Remark.remark_.select_related('consumer', 'commodity').filter(commodity__pk=commodity_pk, is_reward=True)

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

    def update(self, request):
        """更新该用户下购买商品的评论内容，评论状态等"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO 后期利用 gensim 对用户的评论进行分析，符合文明素质用于允许评论
        query_object = self.get_user_remark().filter(is_remark=False)
        if query_object.exists():
            try:
                query_object.update(is_reward=True, **serializer.validated_data)
                return Response(response_code.remark_success, status.HTTP_200_OK)
            except Exception as e:
                evaluate_logger.error(e)
                return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(response_code.has_remarked, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        # TODO 需要仔细去考虑根据remark的id号删，还是根据commodity+user删
        # query_object = self.get_user_remark().filter(is_remark=True)
        # if query_object.exists()

    # def create(self, request):
    #     """评论的创建在用户成功交易完一件商品后创建，设置评论状态为真"""
