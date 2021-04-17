# -*- coding: utf-8 -*-
# @Time  : 2021/2/7 下午4:24
# @Author : 司云中
# @File : carousel_api.py
# @Software: Pycharm

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from shop_app.models.commodity_models import Carousel
from shop_app.serializers.carousel_serializers import CarouselSerializer


class CarouselApiView(GenericAPIView):
    """轮播图操作"""

    serializer_class = CarouselSerializer

    def get_queryset(self):
        return Carousel.objects.all()

    def get(self, request):
        """获取轮播图"""
        serializer = self.get_serializer(instance=self.get_queryset(), many=True)
        return Response(serializer.data)


