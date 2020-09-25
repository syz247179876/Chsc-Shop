# -*- coding: utf-8 -*-
# @Time  : 2020/9/12 下午11:57
# @Author : 司云中
# @File : bonus_api.py
# @Software: Pycharm

from rest_framework.generics import GenericAPIView
from rest_framework.mixins import *
from rest_framework.permissions import IsAuthenticated

from Voucher_app.models.voucher_models import VoucherConsumer

from Voucher_app.serializers.voucher_serializers import  VoucherConsumerSerializer
from e_mall.response_code import response_code


class VoucherOperation(GenericAPIView):
    """优惠卷操作"""

    serializer_class = VoucherConsumerSerializer

    permission_classes = [IsAuthenticated]

    model_class = VoucherConsumer


    def get_queryset(self):
        return self.model_class.voucher_.get_all_voucher(self.request.user)


    def post(self, request):
        """领取优惠卷"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        # 生成优惠卷记录
        instance = self.model_class.voucher_.acquire_coupon(user=request.user, validated_data=serializer.validated_data)

        if instance:
            return Response(response_code.acquire_coupon_success)
        else:
            return Response(response_code.acquire_coupon_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get(self, request, *args, **kwargs):
        """获取该用户下关于该商品或者商家的优惠卷"""

        queryset = self.get_queryset()
        serializer = self.get_serializer(instance=queryset)
        return Response(serializer.data)






