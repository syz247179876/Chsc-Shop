# -*- coding: utf-8 -*-
# @Time  : 2021/2/15 下午7:47
# @Author : 司云中
# @File : manage_role_api.py
# @Software: Pycharm

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Emall.decorator import validate_url_data
from Emall.response_code import response_code
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
        return response_code.add_role_success


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
        return response_code.modify_role_success

    def delete(self, request):
        """删除角色"""
        serializer = self.serializer_delete_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.serializer_class.Meta.model.role_.filter(pk__in=serializer.validated_data.get('pk_list')).delete()
        return response_code.delete_role_success
