import logging

from drf_haystack.viewsets import HaystackViewSet

from Shop_app.redis.shop_cart_redis import ShopRedisCartOperation
from Shop_app.redis.shop_favorites_redis import ShopRedisFavoritesOperation
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from Shop_app.serializers.ShopSearchSerializerApi import ShopSearchSerializer
from e_mall.loggings import Logging
from e_mall.response_code import response_code
from rest_framework import mixins
from rest_framework import generics
from rest_framework import serializers
from Shop_app.models.commodity_models import Commodity
from rest_framework.response import Response
from rest_framework.views import APIView

common_logger = Logging.logger('django')


# class GoodsSerializer(serializers.ModelSerializer):
#     """返回商品"""
#     store_name = serializers.CharField(source='store.store_name', read_only=True)
#     username = serializers.CharField(source='shopper.username', read_only=True)
#     province = serializers.CharField(source='store.province', read_only=True)  # 销售省份
#     city = serializers.CharField(source='store.city', read_only=True)  # 销售城市
#     shop_grade = serializers.DateTimeField(source='store.shop_grade', read_only=True)  # 店铺评分
#     attention = serializers.IntegerField(source='store.attention', read_only=True)  # 关注度
#
#     class Meta:
#         model = Commodity
#         fields = ['store_name', 'username', 'commodity_name', 'price', 'intro', 'category', 'discounts', 'sell_counts',
#                   'province', 'city', 'shop_grade', 'attention']
#
#
# class GoodsIntro(mixins.ListModelMixin,
#                  generics.GenericAPIView):
#     """获取商品列表基本信息"""
#     queryset = Commodity.commodity_.all()
#     serializer_class = GoodsSerializer
#
#     def get(self, request, *args, **kwargs):
#         """获取已上架的所有商品"""
#         category = request.data.get('category')
#         self.queryset = Commodity.commodity_.fliter(status='Onshelve', category=category)
#         return self.list(self, request, *args, **kwargs)


class AddShopCartOperation(APIView):
    """the operation of adding goods into shop cart"""
    redis = ShopRedisCartOperation.choice_redis_db('redis')

    @method_decorator(login_required(login_url='consumer/login/'))
    def post(self, request):
        user = request.user
        data = request.data

        is_add_success = self.redis.add_goods_into_shop_cart(user.pk, **data)

        return Response(response_code.add_goods_into_shop_cart_success) if is_add_success \
            else Response(response_code.add_goods_into_shop_cart_error)


class AddFavoritesOperation(APIView):
    """the operation of adding goods into favorites"""

    redis = ShopRedisFavoritesOperation.choice_redis_db('redis')

    @method_decorator(login_required(login_url='consumer/login/'))
    def post(self, request):
        user = request.user
        data = request.data

        is_add_success = self.redis.add_goods_into_favorites(user.pk, **data)
        return Response(response_code.add_goods_into_favorites_success) if is_add_success \
            else Response(response_code.add_goods_into_favorites_error)


class CommoditySearchOperation(HaystackViewSet):
    """ES搜索操作"""

    index_models = [Commodity]

    serializer_class = ShopSearchSerializer

    def list(self, request, *args, **kwargs):
        # queryset = self.filter_queryset(self.get_queryset())
        #
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)
        #
        # serializer = self.get_serializer(queryset, many=True)
        # return Response(serializer.data)
        queryset = self.get_queryset()
        common_logger.info(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



