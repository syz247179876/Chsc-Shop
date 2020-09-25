# -*- coding: utf-8 -*-
# @Time : 2020/5/25 19:43
# @Author : 司云中
# @File : order.py
# @Software: PyCharm
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError, transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Order_app.pagination import OrderResultsSetPagination
from Order_app.models.order_models import Order_basic
from Order_app.redis.OrderRedis import RedisOrderOperation
from Order_app.serializers.order_serializers import OrderBasicSerializer, OrderCommoditySerializer, \
    OrderAddressSerializer, OrderCreateSerializer
from e_mall.loggings import Logging

from e_mall.response_code import response_code

common_logger = Logging.logger('django')

order_logger = Logging.logger('order_')


class OrderBasicOperation(viewsets.GenericViewSet):
    """订单基本操作"""

    # permission_classes = [IsAuthenticated]

    serializer_class = OrderBasicSerializer

    redis = RedisOrderOperation.choice_redis_db('redis')  # 选择redis具体db

    def get_queryset(self):
        """默认获取该用户的所有订单"""
        return Order_basic.order_basic_.filter(consumer=self.request.user)

    def disguise_del_order_list(self, validated_data):
        """逻辑群删除订单"""
        return self.get_queryset().filter(pk__in=validated_data.get('list_pk', [])).update(delete_consumer=True)

    def substantial_del_order_list(self, validated_data):
        """当用户和商家都已逻辑删除订单，此时群真删订单"""
        self.get_queryset().filter(pk__in=validated_data.get('list_pk', []), delete_shopper=True).delete()

    def disguise_del_order(self):
        """逻辑单删订单"""
        instance = self.get_object()
        instance.delete_consumer = True
        instance.save()

    def substantial_del_order(self):
        """真实单删订单"""
        pk = self.kwargs.get(self.lookup_field)
        self.get_queryset().filter(pk=pk, delete_shopper=True).delete()

    @action(methods=['delete'], detail=False)
    def destroy_multiple(self, request, *args, **kwargs):
        """多删"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        common_logger.info(serializer.validated_data.get('list_pk'))
        if not serializer.validated_data.get('list_pk', None):  # 校验订单必须存在
            return Response({'list_pk': ['该字段必须存在']})
        try:
            with transaction.atomic():  # 开启事务
                is_delete = self.disguise_del_order_list(serializer.validated_data)
                self.substantial_del_order_list(serializer.validated_data)
        except DatabaseError as e:
            order_logger.error(e)
            return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if not is_delete:
            return Response(response_code.delete_order_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(response_code.delete_order_success, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """单删"""
        try:
            with transaction.atomic():  # 开启事务
                self.disguise_del_order()  # 假删
                self.substantial_del_order()  # 真删
        except DatabaseError as e:
            order_logger.error(e)
            return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(response_code.delete_order_success, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """获取具体的单个订单细节"""
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance)
        expire = self.redis.get_ttl('order_{pk}_expire'.format(pk=self.kwargs.get(self.lookup_field)))
        if expire != -1 and expire != -2:
            serializer.data.update({'order_expire': expire})
        return Response(serializer.data)


class OrderListOperation(GenericAPIView):
    """获取具体status状态的订单操作"""

    lookup_field = 'status'
    pagination_class = OrderResultsSetPagination

    serializer_class = OrderBasicSerializer

    def get_queryset(self):
        """根据status返回查询集"""
        status_ = self.kwargs.get(self.lookup_field, '0')
        if status_ == '0':
            return Order_basic.order_basic_.filter(delete_consumer=False)
        return Order_basic.order_basic_.filter(status=status_, delete_consumer=False)

    def get(self, request, *args, **kwargs):
        """
        获取具体status状态的订单集合
        前端url中传递参数名为page
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)  # 返回一个list页对象,默认返回第一页的page对象
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OrderCreateOperation(GenericAPIView):
    """创建初始订单操作"""

    permission_class = [IsAuthenticated]

    serializer_class = OrderCreateSerializer

    redis = RedisOrderOperation.choice_redis_db('redis')

    def post(self, request):
        """创建初始订单"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.create_order(serializer.validated_data, request.user, self.redis)
        if result:
            return Response(response_code.create_order_success, status=status.HTTP_200_OK)
        else:
            return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class OrderBasicOperation(GenericAPIView):
#     """订单操作"""
#
#     serializer_class = OrderBasicSerializer
#
#     ultimate_class = PageSerializer
#
#     page_class = Page
#
#     def get_serializer(self, *args, **kwargs):
#         serializer_class = self.get_serializer_class
#         return serializer_class(*args, **kwargs)
#
#     def get_ultimate_serializer(self, *args, **kwargs):
#         serializer_class = self.get_ultimate_serializer_class
#         return serializer_class(*args, **kwargs)
#
#     @property
#     def get_serializer_class(self):
#         return self.serializer_class
#
#     @property
#     def get_ultimate_serializer_class(self):
#         return self.ultimate_class
#
#     def get_order_and_page(self, user, **data):
#         """获取某用户订单实例和总页大小"""
#         return self.get_serializer_class().get_order_and_page(user, **data)
#
#     @method_decorator(login_required(login_url='/consumer/login/'))
#     def get(self, request):
#         """获取该用户最近的订单"""
#         user = request.user
#         data = request.GET
#         instances, pages = self.get_order_and_page(user, **data)
#         page = Page(page=pages)
#         serializer = self.get_ultimate_serializer(page, context={'serializer': self.get_serializer_class,
#                                                                  'instances': instances})
#         return Response(serializer.data)
#
#     @method_decorator(login_required(login_url='/consumer/login/'))
#     def delete(self, request):
#         """删除订单"""
#         data = request.data
#         # 单删
#         is_success = self.get_serializer_class().delete_order(**data)
#         # 群删
#         if is_success:
#             return Response(response_code.delete_order_success, status=status.HTTP_200_OK)
#         else:
#             return Response(response_code.delete_address_error)


# class OrderLookView(viewsets.ModelViewSet):
#     """订单操作"""
#     serializer_class = Page
#
#     ultimate_class = PageSerializer
#
#     def get_queryset(self):
#         return Order_basic.order_basic_.filter(consumer=self.request.user)
#
#     def list(self, request, *args, **kwargs):
#         """根据订单状态分批列出某用户的订单"""
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             instances, page = self.get_order_and_page(user)
#
#     def get_permissions(self):
#         """根据不同的action设定权限"""
#         global permission_classes
#         if self.action in ['list', 'destroy', 'retrieve']:
#             permission_classes = [IsAuthenticated, ]
#         return [permission() for permission in permission_classes]  # 返回实例化后的权限类，用于循环校验权限


class OrderBuyNow(APIView):
    """订单跳转暂存操作"""

    permission_classes = [IsAuthenticated]

    serializer_address_class = OrderAddressSerializer
    serializer_commodity_class = OrderCommoditySerializer

    @property
    def get_serializer_address_class(self):
        # 地址序列化类
        return self.serializer_address_class

    @property
    def get_serializer_commodity_class(self):
        # 商品序列化类
        return self.serializer_commodity_class

    @method_decorator(login_required(login_url='/consumer/login/'))
    def post(self, request):
        """
        session做中间件用于暂存交易商品基本信息（不包括money)
        解决ajax禁止定向的问题
        """

        # data = json.loads(request.body.decode('utf-8'))  # 解码 + 反序列化
        data = request.data
        try:
            request.session['commodity_list'] = data['commodity_list']
            request.session['counts_list'] = data['counts_list']
            common_logger.info(request.session['commodity_list'])
            common_logger.info(request.session['counts_list'])
            return Response({'code': 666})
        except Exception as e:
            order_logger.error(e)
            return Response({'code': -666})


class OrderCommitOperation(viewsets.ModelViewSet):
    """用户结算商品，生成初始订单"""

    permission_classes = [IsAuthenticated]

    serializer_class = OrderCommoditySerializer

    extra_time = 30  # 订单持续时间30min

    # def get_serializer_context(self):
    #     """递交额外的信息"""
    #     pass

    # @method_decorator(login_required(login_url='/consumer/login/'))
    # def list(self, request, *args, **kwargs):
    #     """get the commodity which consumer intend to buy"""
    #     # 序列化用户订单生成页获取商品信息
    #     try:
    #         commodity_list = request.session['commodity_list']
    #         instances = self.get_serializer_class.get_commodity(commodity_list)
    #         serializer = self.get_serializer(instances, context=self.context(request), many=True)
    #         return Response(serializer.data)
    #     except Exception as e:
    #         order_logger.error(e)
    #         return Response(None)

    def create(self, request, *args, **kwargs):
        """
        从购物车/商品页直接点击结算/购买
        传入相关信息，计算价格，生成未支付订单
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'www': 'www'})
