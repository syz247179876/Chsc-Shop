# -*- coding: utf-8 -*-
# @Time  : 2021/2/15 下午10:19
# @Author : 司云中
# @File : manage_permission_api.py
# @Software: Pycharm

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Emall.decorator import validate_url_data
from Emall.exceptions import SqlServerError
from Emall.response_code import response_code
from manager_app.serializers.permission_serializers import PermissionSerializer
from manager_app.utils.permission import ManagerPermissionValidation


class ManagePermissionApiView(GenericAPIView):
    """管理权限操作"""

    serializer_class = PermissionSerializer

    permission_classes = [IsAuthenticated, ManagerPermissionValidation]

    def get_obj(self, pk):
        """获取权限记录"""
        try:
            return self.serializer_class.Meta.model.manager_permission_.get(pk=pk)
        except self.serializer_class.Meta.model.DoesNotExist:
            raise SqlServerError()

    def get_queryset(self):
        return self.serializer_class.Meta.model.manager_permission_.all()


    def post(self, request):
        """增加权限"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create_permission()
        return response_code.add_permission_success

    @validate_url_data('role', 'rid')
    def delete(self, request, **kwargs):
        """删除权限"""
        rid_list = request.data.get('rid')
        self.serializer_class.Meta.model.manager_permission_.filter(rid__in=rid_list)
        return response_code.delete_permission_success


    def put(self, request):
        """修改权限"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update_permission()
        return response_code.mo

    @validate_url_data('permission', 'pk', null=True)
    def get(self, request):
        """修改权限"""
        pk = request.query_params.get(self.lookup_field, None)
        if pk:
            # 获取单个权限详细信息
            obj = self.get_obj(pk)
            serializer = self.get_serializer(instance=obj)
        else:
            instances = self.get_queryset()
            serializer = self.get_serializer(instance=instances, many=True)
        return Response(serializer.data)





