# -*- coding: utf-8 -*-
# @Time  : 2021/5/3 下午2:46
# @Author : 司云中
# @File : seller_menu_api.py
# @Software: Pycharm

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from seller_app.models import Seller
from seller_app.serializers.menu_serializers import SellerMenuSerializer


class SellerMenuApiView(GenericAPIView):

    serializer_class = SellerMenuSerializer

    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Seller.objects.filter(user=self.request.user).select_related('role').first()

    def get(self, request):
        """获取当前已经登录商家的权限集"""
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data)
