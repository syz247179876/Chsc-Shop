# -*- coding: utf-8 -*-
# @Time  : 2021/1/11 下午5:26
# @Author : 司云中
# @File : information_api.py
# @Software: Pycharm
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Emall.exceptions import UniversalServerError
from Emall.loggings import Logging
from Emall.response_code import response_code
from user_app.model.collection_models import Collection
from user_app.model.foot_models import Foot
from user_app.model.trolley_models import Trolley
from user_app.models import Address
from user_app.redis.foot_redis import foot_redis
from user_app.serializers.individual_info_serializers import IndividualInfoSerializer

consumer_logger = Logging.logger('consumer_')
User = get_user_model()


class InformationOperation(GenericAPIView):
    """
    保存信息
    修改用户名后需重新登录
    """

    permission_classes = [IsAuthenticated]

    serializer_class = IndividualInfoSerializer

    def get_object(self):
        """返回用户对象"""
        return self.request.user

    def get_queryset(self):
        """返回用户对象，join consumer表"""
        return User.objects.filter(pk=self.request.user.pk).select_related('consumer').first()
        # return Consumer.consumer_.filter(user=self.request.user).select_related('user').first()

    def patch(self, request):
        """修改用户名"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.get_object().username = serializer.validated_data.get('username')
            self.get_object().save(update_fields=['username'])
        except Exception as e:
            consumer_logger.error(e)
            raise UniversalServerError()
        else:
            return Response(response_code.user_infor_change_success, status=status.HTTP_200_OK)

    def get(self, request):
        """获取用户详细信息"""
        instance = self.get_queryset()
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data)


class UserExtraInfoOperation(GenericViewSet):
    """获取用户额外信息"""

    permission_classes = [IsAuthenticated]
    # foot_model = Foot
    trolley_model = Trolley
    collection_model = Collection
    address_model = Address

    redis = foot_redis

    def result_data(self, request):
        """
        构建数据集合
        :return dict
        """

        user = request.user
        trolley_dict = self.trolley_model.trolley_.filter(user=user).aggregate(trolley_count=Count('id'))
        collection_dict = self.collection_model.objects.filter(user=user).aggregate(
            collection_count=Count('id'))
        address_dict = self.address_model.address_.filter(user=user).aggregate(address_count=Count('id'))
        return {
            'trolley_count': trolley_dict.get('trolley_count'),
            'collection_count': collection_dict.get('collection_count'),
            'address_count': address_dict.get('address_count'),
            'foot_count': self.foot_count(user)
        }

    def foot_count(self, user):
        return self.redis.retrieve_foot_count(user.pk)

    @method_decorator(cache_page(30))
    @action(methods=['GET'], detail=False, url_path='count')
    def extra_count(self, request):
        """获取用户足迹，收藏夹，购物车，收货地址的数量"""
        data = self.result_data(request)
        consumer_logger.error("老色批")
        return Response(data, status=status.HTTP_200_OK)
