# -*- coding: utf-8 -*-
# @Time  : 2021/2/15 下午7:47
# @Author : 司云中
# @File : manage_role_api.py
# @Software: Pycharm

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Emall.response_code import response_code, ADD_ROLE_SUCCESS, MODIFY_ROLE_SUCCESS, DELETE_ROLE_SUCCESS
from manager_app.serializers.role_serializers import RoleSerializer, RoleDeleteSerializer
from manager_app.utils.permission import ManagerPermissionValidation


class ManageRoleApiView(GenericAPIView):
    """超级管理员角色管理"""

    serializer_class = RoleSerializer
    serializer_delete_class = RoleDeleteSerializer

    permission_classes = [IsAuthenticated, ManagerPermissionValidation]

    def get_queryset(self):
        return self.serializer_class.Meta.model.role_.all()

    def post(self, request):
        """添加角色"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.add_role()
        return Response(response_code.result(ADD_ROLE_SUCCESS, '添加成功'))


    def get(self, request):
        """获取角色"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(instance=queryset, many=True)
        return Response(serializer.data)


    def put(self, request):
        """修改角色"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.modify_role()
        return Response(response_code.result(MODIFY_ROLE_SUCCESS, '修改成功'))

    def delete(self, request):
        """删除角色"""
        serializer = self.serializer_delete_class(data=request.data)
        # 如果url中带有many=true查询参数时,删除全部
        if self.request.query_params.get('all', None) == 'true':
            self.get_queryset().delete()
        else:
            serializer.is_valid(raise_exception=True)
            self.serializer_class.Meta.model.role_.filter(pk__in=serializer.validated_data.get('pk_list')).delete()
        return Response(response_code.result(DELETE_ROLE_SUCCESS, '删除成功'))
