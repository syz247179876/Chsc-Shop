# -*- coding: utf-8 -*-
# @Time  : 2021/4/3 下午4:18
# @Author : 司云中
# @File : manage_seller_api.py
# @Software: Pycharm

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from Emall.response_code import response_code, MODIFY_USER_ROLE, ADD_ROLE_PERMISSION, MODIFY_ROLE_PERMISSION, \
    DELETE_ROLE_PERMISSION
from manager_app.serializers.role_serializers import MRoleSerializer

from manager_app.serializers.permission_serializers import MPermSerializer


class ManagerSellerPermApiView(GenericAPIView):
    """
    管理员管理某个角色/指定商家所属角色下的权限集
    手动分配/修改/删除权限
    """
    serializer_class = MPermSerializer

    def post(self, request):
        """手动为某个角色/指定商家增加权限"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.add()
        return Response(response_code.result(ADD_ROLE_PERMISSION,'添加成功'))

    def put(self, request):
        """手动为某个角色/指定商家修改权限"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.modify()
        return Response(response_code.result(MODIFY_ROLE_PERMISSION, '修改成功'))

    def delete(self, request):
        """手动为某个角色/指定商家删除权限"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.delete()
        return Response(response_code.result(DELETE_ROLE_PERMISSION, '删除成功'))


class ManagerSellerRoleApiView(GenericAPIView):
    """
    管理员管理商家角色
    手动为商家分配/修改/删除角色(目前先在开店阶段将role写死，后期改成由管理员审核分配权限）
    """
    serializer_class = MRoleSerializer

    def put(self, request):
        """手动为所有商家/指定商家修改角色"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rows = serializer.modify()
        return Response(
            response_code.result(MODIFY_USER_ROLE, '修改成功') if rows >= 1 else response_code.result(MODIFY_USER_ROLE,
                                                                                                  '无任何操作'))
