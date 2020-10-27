# -*- coding: utf-8 -*- 
# @Time : 2020/5/29 14:09 
# @Author : 司云中 
# @File : remark_api.py 
# @Software: PyCharm
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from remark_app.models.remark_models import Remark
from remark_app.pagination import RemarkResultsSetPagination
from remark_app.serializers.attitude_action_serializers import AttitudeRemarkSerializer
from remark_app.serializers.user_marker_serializers import UserMarkerSerializer
from remark_app.signals import remark_post, remark_cancel
from Emall.loggings import Logging
from Emall.response_code import response_code

common_logger = Logging.logger('django')

evaluate_logger = Logging.logger('evaluate_')


class RemarkOperation(GenericViewSet):

    permission_classes = [IsAuthenticated]

    serializer_class = UserMarkerSerializer

    pagination_class = RemarkResultsSetPagination

    def get_queryset(self):
        """获取用户所浏览的店铺的评论"""
        commodity_pk = self.kwargs.get('pk')
        return Remark.remark_.select_related('consumer', 'commodity').filter(commodity__pk=commodity_pk, is_remark=True)

    def get_user_remark(self):
        """获取用户对某商品的评论"""
        commodity_pk = self.kwargs.get('pk')
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

    @action(methods=['put'], detail=True)
    def add_remark(self, request, *args, **kwargs):
        """添加评论，实则更新该用户下购买商品的评论内容，评论状态等"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO 后期利用 gensim 对用户的评论进行分析，符合文明素质用于允许评论
        query_object = self.get_user_remark().filter(is_remark=False)
        if query_object.exists():  # 存在机会为True，每个商品只能评论一次
            query_object.update(is_reward=True, **serializer.validated_data)
            remark_post.send(    # 添加评论信号
                sender=type(self),
                commodity_pk=self.kwargs.get('pk'),
                user=request.user
            )
            return Response(response_code.remark_success, status.HTTP_200_OK)
        else:
            return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def destroy(self, request, *args, **kwargs):
        """根据id删除评论"""
        remark_obj = self.get_object()
        is_delete = remark_obj.delete()
        if is_delete:
            remark_cancel.send(   # 取消评论信号，清理缓存
                sender=type(self),
                commodity_pk=self.kwargs.get('pk'),
                user=request.user
            )
            return Response(response_code.delete_order_success, status=status.HTTP_200_OK)
        else:
            return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AttitudeRemarkOperation(GenericViewSet):
    """点赞差评操作类"""

    model = Remark

    serializer_class = AttitudeRemarkSerializer

    permission_classes = [IsAuthenticated]

    def get_model(self):
        return self.model

    def get_obj(self, validated_data):
        try:
            pk = validated_data.get('pk')
            return self.get_model().remark_.get(consumer=self.request.user, pk=pk)
        except self.get_model().DoesNotExist:
            return None

    @action(methods=['patch'],detail=False)
    def remark_click(self, request, *args, **kwargs):
        """点赞/反对"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.get_obj(serializer.validated_data)
        if obj:
            obj = serializer.execute_action(obj)    # 更新后的obj
            serializer = self.get_serializer(instance=obj)  # 序列化obj
            return Response(response_code.add_action_remark_success(serializer.data))
        else:
            return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







