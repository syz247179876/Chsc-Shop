# -*- coding: utf-8 -*-
# @Time  : 2021/1/11 下午5:28
# @Author : 司云中
# @File : favourites_api.py
# @Software: Pycharm
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from Emall.decorator import validate_url_data
from Emall.response_code import response_code, DELETE_FAVORITES_SUCCESS, ADD_FAVORITES_SUCCESS
from user_app.model.collection_models import Collection


# class FavoriteOperation(GenericViewSet):
#     """收藏夹处理"""
#
#     permission_classes = [IsAuthenticated]
#
#     redis = favorites_redis
#
#     serializer_class = FavoritesSerializer  # favorites序列化类
#
#     pagination_class = FavoritesPagination
#
#     def get_queryset(self):
#         """
#         先hit缓存数据库，如果过期则重新添加到缓存中，否则直接从缓存中取
#         :return 结果集/异步任务/空列表 QuerySet/AsyncResult/List
#         """
#         page_size = FootResultsSetPagination.page_size
#         page = self.request.query_params.get(self.pagination_class.page_query_param, 1)  # 默认使用第一页
#         resultSet = self.redis.get_resultSet(self.request.user, page=page, page_size=page_size)
#         return resultSet
#
#     def get_object(self):
#         """
#         查找对应pk的收藏夹记录
#         :return: Model
#         """
#         try:
#             return Collection.objects.get(user=self.request.user, pk=self.kwargs.get('pk'))
#         except Collection.DoesNotExist:
#             raise Http404
#
#     def get_delete_queryset(self):
#         """
#         欲删除指定用户的所有收藏目录
#         :return:结果集合  QuerySet
#         """
#         return Collection.objects.filter(user=self.request.user)
#
#     @method_decorator(cache_page(10 * 1, cache='redis'))
#     def list(self, request):
#         """显示收藏夹的商品"""
#
#         queryset = self.get_queryset()
#
#         if isinstance(queryset, QuerySet):  # 命中数据库
#             page = self.paginate_queryset(queryset)
#             if page is not None:
#                 serializer = self.get_serializer(page, many=True)
#                 return self.get_paginated_response(serializer.data)
#             serializer = self.get_serializer(queryset, many=True)
#             return Response(serializer.data)
#
#         queryset = self.get_queryset()
#         if isinstance(queryset, QuerySet):  # 命中数据库
#             page = self.paginate_queryset(queryset)
#             if page is not None:
#                 serializer = self.get_serializer(page, many=True)
#                 return self.get_paginated_response(serializer.data)
#             serializer = self.get_serializer(queryset, many=True)
#             return Response(serializer.data)
#         # if isinstance(queryset, AsyncResult):   # 命中缓存
#         #     # 最迟2s获取数据
#         #     limit = 2
#         #     while not queryset.get() or limit:  # 轮循一直有结果才返回get()
#         #         time.sleep(1)
#         #         limit -= 1
#         #     return Response(queryset.get())
#         elif isinstance(queryset, str):  # 命中缓存，读取缓存中的数据
#             # 将redis中的序列化数据格式成分页器
#             return Response({'data': queryset})
#         elif isinstance(queryset, list):  # 缓存为空，数据库也为空，防止缓存击穿
#             return Response({'data': queryset})
#         else:
#             common_logger.info(type(queryset))
#             return Response(response_code.verification_code_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#     def create_collection(self, type, queryset):
#         """
#         创建某用户收藏记录
#         :param type: 功能类型 'commodity',  str
#         :param queryset: {'commodity':QuerySet}, dict
#         :return:Bool
#         """
#         queryset = queryset.get(type)  # 为了可序列化，取QuerySet的第一个元素，反正也只有一个
#         try:
#             if queryset:
#                 now = datetime.datetime.now()  # 生产时间戳
#                 queryset_first = {type: queryset.first()}
#                 instance = Collection.objects.create(user=self.request.user, datetime=now, **queryset_first)
#                 add_favorites.send(  # 发送信号，同步redis
#                     sender=Collection,
#                     instance=instance,
#                     user=self.request.user,
#                     queryset=queryset,
#                 )
#                 return True if instance else False
#             else:
#                 return False
#         except Exception as e:
#             consumer_logger.error(e)
#             return False
#
#     def create(self, request):
#         """添加商品到收藏夹"""
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         store, commodity = self.get_serializer_class().get_store_commodity(serializer.validated_data)
#         is_created = False
#         if store:
#             is_created = self.create_collection('store', {'store': store})
#         elif commodity:
#             is_created = self.create_collection('commodity', {'commodity': commodity})
#         if is_created:
#             return Response(response_code.add_favorites_success)
#         else:
#             raise Http404
#
#     def destroy(self, request, *args, **kwargs):
#         """单删收藏夹商品"""
#         obj = self.get_object()
#         is_deleted, delete_dict = obj.delete()
#         if is_deleted:
#             # 发送删除收藏夹商品的信号
#             delete_favorites.send(
#                 sender=Collection,
#                 user=self.request.user,
#                 collection_pk=self.kwargs.get('pk'),
#                 is_all=False
#             )
#             return Response(response_code.delete_favorites_success)
#         else:
#             return Response(response_code.delete_favorites_error)
#
#     @action(methods=['delete'], detail=False)
#     def destroy_all(self, request):
#         """全删收藏夹"""
#         queryset = self.get_delete_queryset()
#         delete_counts, dict_delete = queryset.delete()
#         if delete_counts:
#             delete_favorites.send(
#                 sender=Collection,
#                 user=self.request.user,
#                 is_all=True
#             )
#             return Response(response_code.delete_favorites_success)
#         else:
#             return Response(status=status.HTTP_204_NO_CONTENT)  # 无响应内容，避免显示已删除
from user_app.serializers.favorites_serializers import FavoritesSerializer


class FavoritesOperation(GenericViewSet):
    """收藏夹相关API"""
    permission_classes = [IsAuthenticated]
    serializer_class = FavoritesSerializer

    def get_queryset(self):
        """返回用户的收藏夹信息"""
        return Collection.objects.select_related('commodity').filter(user=self.request.user)

    def list(self, request):
        """
        获取用户收藏的商品
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(instance=queryset, many=True)
        return Response(serializer.data)

    @validate_url_data('favorites', 'pk')
    def destroy(self, request, **kwargs):
        """删除一条收藏记录"""
        pk, user = kwargs.get('pk'), request.user
        rows, _ = Collection.objects.filter(pk=pk, user=user).delete()
        return Response(response_code.result(DELETE_FAVORITES_SUCCESS, '删除成功' if rows > 0 else '无数据操作'))

    @action(methods=['delete'], detail=False, url_path='destroy-all')
    def destroy_all(self, request):
        """删除全部收藏记录"""
        rows, _ = Collection.objects.filter(user=request.user).delete()
        return Response(response_code.result(DELETE_FAVORITES_SUCCESS, '删除成功' if rows > 0 else '无数据操作'))

    def create(self, request):
        """添加收藏记录"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = serializer.add(request)
        return Response(response_code.result(ADD_FAVORITES_SUCCESS, '添加成功' if res else '无数据更新', data=res.pk))

