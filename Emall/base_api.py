# -*- coding: utf-8 -*-
# @Time  : 2020/11/21 上午11:27
# @Author : 司云中
# @File : base_api.py
# @Software: Pycharm

"""
通用API共享函数
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from Emall.response_code import response_code


def check_code(redis, validated_data):
    """校验验证码"""
    code_status = redis.check_code(validated_data.get('phone'), validated_data.get('code'))
    # 验证码错误或者过期
    if not code_status:
        return Response(response_code.verification_code_error, status=status.HTTP_400_BAD_REQUEST)


class BackendGenericApiView(GenericAPIView):
    """用于后台操作的通用API"""

    serializer_class = None

    serializer_delete_class = None


    def post(self, request):
        """添加"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.add()

    def get(self, request):
        """获取单个/多个记录"""
        pk = request.query_params.get('pk', None)
        if request.query_params.get('pk', None):
            instance = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(instance=instance)
        else:
            instance = self.get_queryset()
            serializer = self.get_serializer(instance=instance, many=True)
        return Response(serializer.data)

    def put(self, request):
        """修改"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        serializer.modify()

    def delete(self, request):
        """删除"""
        serializer = self.serializer_delete_class(data=request.data)
        if self.request.query_params.get('all', None) == 'true':
            serializer.delete()
        else:
            serializer.is_valid(raise_exception=True)
            serializer.delete()