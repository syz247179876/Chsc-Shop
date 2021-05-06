# -*- coding: utf-8 -*-
# @Time : 2020/5/25 19:43
# @Author : 司云中
# @File : order.py
# @Software: PyCharm
from django.db import DatabaseError, transaction
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Emall.exceptions import SqlServerError, DataNotExist
from Emall.loggings import Logging
from Emall.response_code import response_code, DELETE_ORDER_SUCCESS, CREATE_ORDER_SUCCESS, ACCEPT_ORDER
from order_app.models.order_models import OrderBasic, OrderDetail
from order_app.redis.order_redis import order_redis
from order_app.serializers.order_serializers import OrderBasicSerializer, OrderCreateSerializer, OrderConfirmSerializer, \
    OrderSellerSerializer
from user_app.model.trolley_models import Trolley

common_logger = Logging.logger('django')

order_logger = Logging.logger('order_')


class OrderBasicOperation(viewsets.GenericViewSet):
    """订单基本操作"""

    permission_classes = [IsAuthenticated]

    serializer_class = OrderBasicSerializer

    serializer_seller_class = OrderSellerSerializer

    serializer_create_class = OrderCreateSerializer

    redis = order_redis

    def get_object_detail(self):
        """获取某个订单及订单下的商品信息"""
        pass

    def get_create_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_create_class(*args, **kwargs)

    def get_queryset(self):
        """默认获取该用户的所有订单"""
        return OrderDetail.order_detail_.filter(user=self.request.user).select_related('order_basic')

    def get_status_queryset(self):
        """根据订单状态搜索数据集"""
        status = self.request.query_params.get('status', '0')
        if status == '0':
            return OrderBasic.order_basic_.filter(user=self.request.user, delete_consumer=False). \
                prefetch_related('order_details').prefetch_related('order_details__commodity__store'). \
                prefetch_related('order_details__sku')
        return OrderBasic.order_basic_.filter(user=self.request.user, status=status, delete_consumer=False). \
            prefetch_related('order_details').prefetch_related('order_details__commodity__store'). \
            prefetch_related('order_details__sku')

    def get_seller_queryset(self):
        """
        返回商家所需要的订单信息，获取订单中属于商家店铺下的商品
        """
        return OrderDetail.order_detail_.filter(user=self.request.user).select_related('order_basic__address',
                                                                                       'commodity', 'sku'). \
            filter(delete_seller=False)

    def disguise_del_order_list(self, validated_data):
        """
        商家逻辑群删除订单
        :return int
        """
        identity = validated_data.get('identity')
        if identity == -1:
            return self.get_queryset().filter(pk__in=validated_data.get('pk_list', [])).select_related('user').\
                filter(user__is_seller=False).update(delete_consumer=True)
        elif identity == 1:
            return self.get_queryset().filter(pk__in=validated_data.get('pk_list', [])).select_related('user').\
                filter(user__is_seller=True).update(delete_seller=True)

    def substantial_del_order_list(self, validated_data):
        """
        当用户和商家都已逻辑删除订单，此时群真删订单
        :return int
        """
        rows, _ = self.get_queryset().filter(pk__in=validated_data.get('pk_list', []), delete_seller=True, delete_consumer=True).delete()
        return rows

    def disguise_del_order(self, identity):
        """逻辑单删订单"""
        instance = self.get_object()
        print(instance.delete_seller)
        if identity == -1:
            instance.delete_consumer = True
            instance.save(update_fields=['delete_consumer'])
        elif identity == 1:
            instance.delete_seller = True
            instance.save(update_fields=['delete_seller'])
            print(instance.delete_seller)

    def substantial_del_order(self):
        """真实单删订单"""
        pk = self.kwargs.get(self.lookup_field)
        self.get_queryset().filter(pk=pk, delete_seller=True, delete_consumer=True).delete()

    @action(methods=['delete'], detail=False, url_path='delete-multiple')
    def destroy_multiple(self, request, *args, **kwargs):
        """多删"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data.get('pk_list', None) or not serializer.validated_data.get('identity', None):  # 校验订单必须存在
            raise DataNotExist('缺少数据')
        try:
            with transaction.atomic():  # 开启事务
                is_delete = self.disguise_del_order_list(serializer.validated_data)
                self.substantial_del_order_list(serializer.validated_data)
        except DatabaseError as e:
            order_logger.error(e)
            raise SqlServerError()
        else:
            return Response(response_code.result(DELETE_ORDER_SUCCESS, '删除成功' if is_delete else '无数据修改'))

    def destroy(self, request, pk=None):
        """
        用户/商家单删订单
        只有当两者都删除后才真正删除
        """
        identity = request.query_params.get('identity', None)
        if not identity:
            raise DataNotExist('缺少数据')
        try:
            with transaction.atomic():  # 开启事务
                self.disguise_del_order(int(identity))  # 假删
                self.substantial_del_order()  # 真删
        except DatabaseError as e:
            order_logger.error(e)
            raise SqlServerError()
        else:
            return Response(response_code.result(DELETE_ORDER_SUCCESS, '删除成功'))

    def retrieve(self, request, pk=None):
        """获取具体的单个订单细节"""
        obj = self.get_object_detail()
        serializer = self.get_serializer(instance=obj)
        # 检查某个订单是否过期
        expire = self.redis.get_ttl('order_{pk}_expire'.format(pk=self.kwargs.get(self.lookup_field)))
        if expire != -1 and expire != -2:
            serializer.data.update({'order_expire': expire})  # 返回过期时间
            return Response(serializer.data)
        else:
            return Response({'detail': '订单已经失效'})

    def list(self, request, *args, **kwargs):
        """
        获取具体status状态的订单集合
        前端url中传递参数名为page
        """
        queryset = self.get_status_queryset()
        page = self.paginate_queryset(queryset)  # 返回一个list页对象,默认返回第一页的page对象
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """创建初始订单"""
        serializer = self.get_create_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create_order(request.user, self.redis)
        return Response(response_code.result(CREATE_ORDER_SUCCESS, '创建成功'))

    @action(methods=['GET'], detail=False, url_path='seller')
    def seller_list(self, request):
        """为商家展示对应的订单信息"""
        queryset = self.get_seller_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_seller_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.serializer_seller_class(instance=queryset, many=True)
        return Response({
            'count': queryset.count(),
            'data': serializer.data
        })

    @action(methods=['PUT'], detail=True, url_path='reception')
    def seller_accept_order(self, request, pk):
        """商家接受订单"""
        rows = OrderDetail.order_detail_.filter(pk=pk, user=request.user).update(is_checked=True)
        return Response(response_code.result(ACCEPT_ORDER, '接单成功' if rows else '无效操作'))


class OrderConfirmOperation(GenericAPIView):
    """
    用户点击结算/立即购买
    进入确认订单步骤
    """
    permission_classes = [IsAuthenticated]

    serializer_class = OrderConfirmSerializer

    def get_instance(self, pk_list):
        return Trolley.trolley_.filter(pk__in=pk_list, user=self.request.user).select_related('commodity__store'). \
            select_related('commodity__freight').select_related('sku')

    def post(self, request):
        """根据用户结算时选择的商品进行显示"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer = self.get_serializer(instance=self.get_instance(serializer.validated_data.get('pk_list')),
                                         many=True)
        return Response(serializer.data)

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
#         return OrderBasic.order_basic_.filter(consumer=self.request.user)
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

#
# class OrderBuyNow(APIView):
#     """订单跳转暂存操作"""
#
#     permission_classes = [IsAuthenticated]
#
#     serializer_address_class = OrderAddressSerializer
#     serializer_commodity_class = OrderCommoditySerializer
#
#     @property
#     def get_serializer_address_class(self):
#         # 地址序列化类
#         return self.serializer_address_class
#
#     @property
#     def get_serializer_commodity_class(self):
#         # 商品序列化类
#         return self.serializer_commodity_class
#
#     @method_decorator(login_required(login_url='/consumer/login/'))
#     def post(self, request):
#         """
#         session做中间件用于暂存交易商品基本信息（不包括money)
#         解决ajax禁止定向的问题
#         """
#
#         # data = json.loads(request.body.decode('utf-8'))  # 解码 + 反序列化
#         data = request.data
#         try:
#             request.session['commodity_list'] = data['commodity_list']
#             request.session['counts_list'] = data['counts_list']
#             common_logger.info(request.session['commodity_list'])
#             common_logger.info(request.session['counts_list'])
#             return Response({'code': 666})
#         except Exception as e:
#             order_logger.error(e)
#             return Response({'code': -666})
#
#
# class OrderCommitOperation(viewsets.ModelViewSet):
#     """用户结算商品，生成初始订单"""
#
#     permission_classes = [IsAuthenticated]
#
#     serializer_class = OrderCommoditySerializer
#
#     extra_time = 30  # 订单持续时间30min
#
#     # def get_serializer_context(self):
#     #     """递交额外的信息"""
#     #     pass
#
#     # @method_decorator(login_required(login_url='/consumer/login/'))
#     # def list(self, request, *args, **kwargs):
#     #     """get the commodity which consumer intend to buy"""
#     #     # 序列化用户订单生成页获取商品信息
#     #     try:
#     #         commodity_list = request.session['commodity_list']
#     #         instances = self.get_serializer_class.get_commodity(commodity_list)
#     #         serializer = self.get_serializer(instances, context=self.context(request), many=True)
#     #         return Response(serializer.data)
#     #     except Exception as e:
#     #         order_logger.error(e)
#     #         return Response(None)
#
#     def create(self, request, *args, **kwargs):
#         """
#         从购物车/商品页直接点击结算/购买
#         传入相关信息，计算价格，生成未支付订单
#         """
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         return Response({'www': 'www'})
