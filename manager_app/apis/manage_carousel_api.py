# -*- coding: utf-8 -*-
# @Time  : 2021/4/6 下午8:51
# @Author : 司云中
# @File : manage_carousel_api.py
# @Software: Pycharm
from rest_framework.response import Response

from Emall.base_api import BackendGenericApiView
from Emall.decorator import validate_url_data
from Emall.response_code import response_code, DELETE_CAROUSEL, ADD_CAROUSEL
from manager_app.serializers.carousel_serializers import ManagerCarouselSerializer,DeleteCarouselSerializer


class ManageCarouselApiView(BackendGenericApiView):
    """管理员管理轮播图API"""

    serializer_class = ManagerCarouselSerializer

    serializer_delete_class = DeleteCarouselSerializer

    def post(self, request):
        """增加轮播图"""
        super().post(request)
        return Response(response_code.result(ADD_CAROUSEL, '添加成功'))

    def delete(self, request):
        """删除轮播图"""
        rows = super().delete(request)
        print(rows)
        return Response(response_code.result(DELETE_CAROUSEL, '删除成功' if rows > 0 else '无数据操作'))

    @validate_url_data('carousel', 'pk')
    def put(self, request):
        """修改轮播图"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rows = serializer.modify()
        return Response(response_code.result(DELETE_CAROUSEL, '修改成功' if rows > 0 else '无数据操作'))

    @validate_url_data('carousel', 'pk', null=True)
    def get(self, request):
        """获取全部轮播图"""
        return super().get(request)



