# -*- coding: utf-8 -*-
# @Time  : 2021/1/11 下午5:05
# @Author : 司云中
# @File : address_api.py
# @Software: Pycharm
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Emall.decorator import validate_url_data
from Emall.loggings import Logging
from Emall.response_code import response_code
from user_app.models import Address
from user_app.serializers.address_serializers import AddressSerializers

consumer_logger = Logging.logger('consumer_')


class AddressOperation(viewsets.ModelViewSet):
    """
    收货地址处理
    """

    # 该属性不仅帮助依照相应的字段筛选出一个对象，还为ViewSet中动态创建URLConf模式时所设定查询字符串
    # 例如以下lookup_field中设置为'user',则生成的URL为/consumer/address-chsc-api/{user}/
    # 映射到相应视图中的参数名也为user

    permission_classes = [IsAuthenticated]

    serializer_class = AddressSerializers

    def get_queryset(self):
        """获取具体某个用户的所有收货地址,搭配List和Retrieve"""
        # APIView重新封装过了request，因此self.request
        return Address.address_.filter(user=self.request.user)

    @validate_url_data('address', 'pk')
    def get_pk(self, **kwargs):
        return kwargs.get('pk')

    # action中的detail用于标识为装饰的视图生成{view_name:url}的有序字典映射
    # 将url和视图绑定
    # @method_decorator(login_required(login_url='consumer/login/'))

    @action(methods=['put'], detail=True)
    def update_default_address(self, request, **kwargs):
        """
        单修改默认地址
        以字典形式传过来的
        """
        self.get_serializer_class().update_default_address(self.get_queryset(), self.get_pk(**kwargs))
        return Response(status=status.HTTP_204_NO_CONTENT)

    @validate_url_data('address', 'pk')
    def update(self, request, *args, **kwargs):
        """单修改地址信息"""
        pk = kwargs.get('pk')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update_address(self.get_queryset(), serializer.validated_data, pk)
        return Response(response_code.modify_address_success, status=status.HTTP_200_OK)

    # 默认与post绑定，反射到post=>post映射到create
    # @method_decorator(login_required(login_url='consumer/login/'))
    def create(self, request, *args, **kwargs):
        """单添加地址"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.add_or_edit_address(self.get_queryset(), request.user, serializer.validated_data)
        return Response(response_code.address_add_success, status=status.HTTP_200_OK)

    # @method_decorator(login_required(login_url='consumer/login/'))
    @validate_url_data('address', 'pk')
    def destroy(self, request, *args, **kwargs):
        """单删除地址DELETE请求"""
        pk = kwargs.get('pk')
        self.get_serializer_class().delete_address(self.get_queryset(), pk)
        return Response(response_code.delete_address_success, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """查看收货地址"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
