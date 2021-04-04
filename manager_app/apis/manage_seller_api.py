# -*- coding: utf-8 -*-
# @Time  : 2021/4/3 下午4:18
# @Author : 司云中
# @File : manage_seller_api.py
# @Software: Pycharm

from rest_framework.generics import GenericAPIView

from manager_app.serializers.role_serializers import MRoleSerializer

from manager_app.serializers.permission_serializers import MPermSerializer


class ManagerSellerPermApiView(GenericAPIView):
    """
    管理员管理商家权限
    手动为商家分配/修改/删除权限
    """
    serializer_class = MPermSerializer

    def post(self):
        """手动为所有商家/指定商家增加权限"""
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.add()

    def put(self):
        """手动为指定商家修改权限"""
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.modify()

    def delete(self):
        """手动为制定商家删除权限"""
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.delete()

    def get(self):
        """搜索获取所有商家/指定的权限信息"""
        pass


class ManagerSellerRoleApiView(GenericAPIView):
    """
    管理员管理商家角色
    手动为商家分配/修改/删除角色(目前先在开店阶段将role写死，后期改成由管理员审核分配权限）
    """
    serializer_class = MRoleSerializer

    def put(self):
        """手动为所有商家/指定商家修改角色"""
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.modify()

    def delete(self):
        """手动为所有商家/制定商家删除角色"""
        pass

    def get(self):
        """获取所有商家/制定的角色信息"""
        pass

