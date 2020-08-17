# -*- coding: utf-8 -*-
# @Time : 2020/5/5 18:42
# @Author : 司云中
# @File : personal_api.py
# @Software: PyCharm
import datetime
import importlib

from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from User_app.models.user_models import Address, Consumer
from User_app.redis.favorites_redis import RedisFavoritesOperation
from User_app.redis.foot_redis import FootRedisOperation
from User_app.redis.shopcart_redis import ShopCartRedisOperation

from User_app.serializers.BindEmailOrPhoneSerializersApi import BindPhoneOrEmailSerializer
from User_app.serializers.FavoritesSerializersApi import FavoritesSerializer
from User_app.serializers.AddressSerializerApi import AddressSerializers

from User_app.redis.user_redis import RedisUserOperation
from User_app.serializers.FootSerializerApi import FootSerializer
from User_app.serializers.IndividualInfoSerializerApi import IndividualInfoSerializer, HeadImageSerializer, \
    VerifyIdCardSerializer
from User_app.serializers.PageSerializerApi import Page, PageSerializer
from User_app.serializers.PasswordSerializerApi import PasswordSerializer
from User_app.serializers.ShopCartSerializerApi import ShopCartSerializer
from User_app.views.ali_card_ocr import Interface_identify
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction, DatabaseError
from django.utils.decorators import method_decorator
from e_mall.loggings import Logging
from e_mall.response_code import response_code
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from django.conf import settings

common_logger = Logging.logger('django')
consumer_logger = Logging.logger('consumer_')


class HeadImageOperation(GenericAPIView):
    """
    修改头像
    """
    permission_classes = [IsAuthenticated]

    serializer_class = HeadImageSerializer

    storage_class = settings.DEFAULT_FILE_STORAGE

    def get_storage_class(self):
        return self.storage_class

    def get_storage(self, *args, **kwargs):
        module_path, class_name = self.get_storage_class().rsplit('.', 1)
        storage = getattr(importlib.import_module(module_path), class_name)
        return storage(**kwargs)

    def get_object(self):
        try:
            return Consumer.consumer_.get(user=self.request.user)
        except Consumer.DoesNotExist:
            raise Http404

    def put(self, request):
        """修改头像"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_modify = serializer.update_head_image(self.get_object(), serializer.validated_data, self.get_storage())
        if is_modify:
            return Response(response_code.modify_head_image_success, status=status.HTTP_200_OK)
        else:
            return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SaveInformation(GenericAPIView):
    """
    保存信息
    修改用户名后需重新登录
    """

    permission_classes = [IsAuthenticated]

    serializer_class = IndividualInfoSerializer

    def get_object(self):
        """返回用户对象"""
        return self.request.user

    def patch(self, request):
        """修改用户名"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.get_object().username = serializer.validated_data.get('username')
            self.get_object().save(update_fields=['username'])
        except Exception as e:
            consumer_logger.error(e)
            return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(response_code.user_infor_change_success, status=status.HTTP_200_OK)

    def get(self, request):
        """获取用户详细信息"""
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data)


class ChangePassword(GenericAPIView):
    """
    修改当前用户的密码
    """

    permission_classes = [IsAuthenticated]

    serializer_class = PasswordSerializer

    redis = RedisUserOperation.choice_redis_db('redis')

    def get_object(self):
        """返回用户对象"""
        return self.request.user

    @property
    def get_object_username(self):
        """获取用户名"""
        return self.request.user.get_username()

    def modify_password(self, user, validated_data):
        """改变用户的密码"""
        old_password = validated_data.get('old_password')
        new_password = validated_data.get('new_password')
        code = validated_data.get('code')
        is_code_checked = self.redis.check_code(self.get_object_username, code)
        is_checked = user.check_password(old_password)  # 核查旧密码
        if not is_code_checked:
            # 验证码不正确
            return Response(response_code.verification_code_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif not is_checked:
            # 旧密码不正确
            return Response(response_code.user_original_password_error,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            user.set_password(new_password)  # 设置新密码
            try:
                user.save(update_fields=["password"])
            except Exception:
                return Response(response_code.modify_password_verification_error,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(response_code.modify_password_verification_success, status=status.HTTP_200_OK)

    def patch(self, request):
        """处理用户密码"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.modify_password(self.get_object(), serializer.validated_data)


class BindEmailOrPhone(GenericAPIView):
    """
    绑定（改绑）用户邮箱或者手机号
    需发送验证码验证
    """

    permission_classes = [IsAuthenticated]

    redis = RedisUserOperation.choice_redis_db('redis')  # 选择配置文件中的redis

    serializer_class = BindPhoneOrEmailSerializer

    def factory(self, way, serializer, instance):
        """简单工厂管理手机号和邮箱的改绑"""
        func_list = {
            'email': 'bind_email',
            'phone': 'bind_phone',
        }
        func = func_list.get(way)
        bind = getattr(serializer, func)
        return bind(self.redis, instance, serializer.validated_data)

    def put(self, request):
        """改绑OR绑定用户的手机或者邮箱"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 校验成功
        way = serializer.validated_data.get('way')
        if way == 'phone':
            instance = Consumer.consumer_.get(user=request.user)
            bind_success = self.factory(way, serializer, instance)
            # 改绑成功bind_email
            if bind_success:
                return Response(response_code.bind_phone_success, status=status.HTTP_200_OK)
            # 改绑失败
            return Response(response_code.bind_email_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            instance = request.user
            bind_success = self.factory(way, serializer, instance)
            if bind_success:
                return Response(response_code.bind_email_success, status=status.HTTP_200_OK)
            return Response(response_code.bind_email_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyIdCard(GenericAPIView):
    """OCR身份识别验证"""

    permission_classes = [IsAuthenticated]

    serializer_class = VerifyIdCardSerializer

    def get_object(self):
        """获取inner join的用户对象"""
        return Consumer.consumer_.select_related('user').get(user=self.request.user)  # 如果没有对象在权限会那抛出404

    def put(self, request):
        """处理POST请求"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_update = serializer.update(self.get_object(), serializer.validated_data)
        if is_update:
            return Response(response_code.verify_id_card_success, status=status.HTTP_200_OK)
        return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

    # action中的detail用于标识为装饰的视图生成{view_name:url}的有序字典映射
    # 将url和视图绑定
    # @method_decorator(login_required(login_url='consumer/login/'))
    @action(methods=['put'], detail=True)
    def update_default_address(self, request, *args, **kwargs):
        """
        单修改默认地址
        以字典形式传过来的
        """
        if self.get_serializer_class().update_default_address(self.get_queryset(), kwargs.get('pk')):
            return Response(response_code.modify_default_success, status=status.HTTP_200_OK)
        return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # @method_decorator(login_required(login_url='consumer/login/'))
    def update(self, request, *args, **kwargs):
        """单修改地址信息"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.update_address(self.get_queryset(), serializer.validated_data, kwargs.get('pk')):
            return Response(response_code.modify_address_success, status=status.HTTP_200_OK)
        return Response(response_code.modify_default_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 默认与post绑定，反射到post=>post映射到create
    # @method_decorator(login_required(login_url='consumer/login/'))

    def create(self, request, *args, **kwargs):
        """单添加地址"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.add_or_edit_address(self.get_queryset(), request.user, serializer.validated_data):
            return Response(response_code.address_add_success, status=status.HTTP_200_OK)
        return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # @method_decorator(login_required(login_url='consumer/login/'))
    def destroy(self, request, *args, **kwargs):
        """单删除地址DELETE请求"""
        if self.get_serializer_class().delete_address(self.get_queryset(), kwargs.get('pk')):
            return Response(response_code.delete_address_success, status=status.HTTP_200_OK)
        return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FavoriteOperation(APIView):
    """
    收藏夹处理
    """

    permission_classes = [IsAuthenticated]

    redis = RedisFavoritesOperation.choice_redis_db('redis')

    serializer_class = FavoritesSerializer  # favorites序列化类

    ultimate_class = PageSerializer  # 页序列化类

    def context(self, instances):
        """额外context数据"""
        return {'instances': instances, 'serializer': self.get_serializer_class}

    def get_serializer(self, *args, **kwargs):
        """产生序列化对象"""
        serializer_class = self.get_serializer_class
        return serializer_class(*args, **kwargs)

    def get_ultimate_serializer(self, *args, **kwargs):
        serializer_class = self.get_ultimate_serializer_class
        return serializer_class(*args, **kwargs)

    @property
    def get_ultimate_serializer_class(self):
        return self.ultimate_class

    @property
    def get_serializer_class(self):
        return self.serializer_class

    def get_favorites(self, favorites_list, **kwargs):
        """收藏夹商品查集对象"""
        return self.get_serializer_class.get_favorites(favorites_list, **kwargs)

    @method_decorator(login_required(login_url='consumer/login/'))
    # @method_decorator(cache_page(10 * 1, cache='redis'))
    def get(self, request):
        """
        处理查询收藏夹GET请求
        返回格式例如：
        {
           'page':3,
           'data':[
           {
             'pk':1,
             'store_name':'小司店铺',
             ...
           },
           {
             'pk':1,
             'store_name':'小云店铺',
             ...
           },
           ...
           ]
        }
        """
        try:
            user = request.user
            data = request.GET
            favorites_list, page = self.redis.get_favorites_goods_id_and_page(user.pk, **data)  # redis获取商品id和最大页数
            instances = self.get_favorites(favorites_list)  # generate instances of commodity
            # generate instance of serializer
            page = Page(page=page)
            serializer = self.get_ultimate_serializer(page, context=self.context(instances))
            return Response(serializer.data)
        except Exception as e:
            consumer_logger.error(e)
        return Response(None)

    # @method_decorator(login_required(login_url='consumer/login/'))
    # def post(self, request):
    #     """add single commodity to consumer favorites"""
    #     user = request.user
    #     data = request.data
    #     is_success = self.redis.add_favorites_goods_id(user.pk, **data)
    #     if is_success:
    #         return Response(response_code.add_favorites_success)
    #     else:
    #         return Response(response_code.add_favorites_error)

    @method_decorator(login_required(login_url='consumer/login/'))
    def delete(self, request):
        """delete single or the whole favorites"""
        user = request.user
        data = request.data
        is_success = self.redis.delete_favorites_goods_id(user.pk, **data)
        if is_success:
            return Response(response_code.delete_favorites_success)
        else:
            return Response(response_code.delete_favorites_error)


class FootOperation(APIView):
    """浏览足迹处理"""

    permission_classes = [IsAuthenticated]

    redis = FootRedisOperation.choice_redis_db('redis')

    serializer_class = FootSerializer  # 序列化器

    ultimate_class = PageSerializer

    def context(self, instances):
        return {'instances': instances, 'serializer': self.get_serializer_class}

    @property
    def get_serializer_class(self):
        return self.serializer_class

    @property
    def get_ultimate_serializer_class(self):
        return self.ultimate_class

    def get_serializer(self, *args, **kwargs):
        serializer = self.get_serializer_class
        return serializer(*args, **kwargs)

    def get_ultimate_serializer(self, *args, **kwargs):
        serializer = self.get_ultimate_serializer_class
        return serializer(*args, **kwargs)

    # @method_decorator(login_required(login_url='consumer/login/'))
    # def post(self, request):
    #     """add footprints"""
    #     user = request.user
    #     data = request.data
    #     is_success = self.redis.add_foot_commodity_id(user.pk, data)
    #     return Response(response_code.add_foot_success) if is_success else Response(response_code.add_foot_error)

    @method_decorator(login_required(login_url='consumer/login/'))
    # @method_decorator(cache_page(30, cache='redis'))
    def get(self, request):
        """
        处理查询收藏夹GET请求
        返回格式例如：
        {
           'page':2,
           'data':[
           {
             'commodity_name':'衬衫',
             'price':'125',
             'intro':'酷～',
             'time':'2020-04-05',
             ...
           },
           {
             'commodity_name':'袜子',
             'price':'15',
             'intro':'纯棉～',
             'time':'2020-04-06',
             ...
           },
           ...
           ]
        }
        """
        try:
            user = request.user
            data = request.GET
            footprints, page = self.redis.get_foot_commodity_id_and_page(user.pk, **data)
            instances = self.get_serializer_class.get_foot(footprints)
            page = Page(page)
            serializer = self.get_ultimate_serializer_class(page, context=self.context(instances))
            return Response(serializer.data)
        except Exception as e:
            consumer_logger.error(e)
            return Response(None)

    @method_decorator(login_required(login_url='consumer/login/'))
    def delete(self, request):
        """delete footprints"""
        user = request.user
        data = request.data
        is_success = self.redis.delete_foot_commodity_id(user.pk, data)
        return Response(response_code.delete_foot_success) if is_success else Response(response_code.delete_foot_error)


class ShopCartOperation(APIView):
    """购物车的相关操作"""

    permission_classes = [IsAuthenticated]

    redis = ShopCartRedisOperation.choice_redis_db('redis')

    serializer_class = ShopCartSerializer  # 序列化器

    ultimate_class = PageSerializer

    def context(self, instances, store_commodity_dict, commodity_and_store, commodity_and_price):
        return {'instances': instances, 'serializer': self.get_serializer_class,
                'context': {'store_and_commodity': store_commodity_dict,
                            'commodity_and_store': commodity_and_store,
                            'commodity_and_price': commodity_and_price}}

    @property
    def get_serializer_class(self):
        return self.serializer_class

    @property
    def get_ultimate_serializer_class(self):
        return self.ultimate_class

    def get_serializer(self, *args, **kwargs):
        serializer = self.get_serializer_class
        return serializer(*args, **kwargs)

    def get_ultimate_serializer(self, *args, **kwargs):
        serializer = self.get_ultimate_serializer_class
        return serializer(*args, **kwargs)

    @method_decorator(login_required(login_url='consumer/login/'))
    def get(self, request):
        """
        查询购物车相关商品GET请求
        格式如下：
{
    "page": 2,
    "data": [
        {
            "commodity_name": "旺仔牛奶",
            "grade": "四星好评",
            "reward_content": "宝贝非常好，质量不错，下次继续买你家的，不过物流太慢了，好几天才到！",
            "reward_time": "2020-05-29T15:20:53",
            "price": 5,
            "category": "食品",
            "image": null
        },
        {
            "commodity_name": "鹿皮棉袄",
            "grade": "四星好评",
            "reward_content": "宝贝非常好，质量不错，下次继续买你家的，不过物流太慢了，好几天才到！",
            "reward_time": "2020-05-28T15:20:53",
            "price": 300,
            "category": "衣服",
            "image": null
        },
    ]
}
        """

        try:
            user = request.user
            data = request.GET
            # retrieve information based on dict form and page(int)
            store_commodity_dict, price_commodity_dict, commodity_counts_dict, page = \
                self.redis.get_shop_cart_id_and_page(user.pk, **data)
            # generate instances of store
            store_instances = self.get_serializer_class.get_stores(store_commodity_dict.keys())
            page = Page(page)
            # 这里序列化器嵌套调用
            serializer = self.get_ultimate_serializer_class(page,
                                                            context=self.context(store_instances, store_commodity_dict,
                                                                                 commodity_counts_dict,
                                                                                 price_commodity_dict))
            return Response(serializer.data)
        except Exception as e:
            consumer_logger.error(e)
            return Response(None)

    # @method_decorator(login_required(login_url='consumer/login/'))
    # def post(self, request):
    #     """add new goods into shop cart under the account of consumer who send request"""
    #     pass

    @method_decorator(login_required(login_url='consumer/login/'))
    def put(self, request):
        """修改购物车的商品的数量PUT请求"""
        user = request.user
        data = request.data
        is_success = self.redis.edit_one_good(user.pk, **data)
        if is_success:
            return Response(response_code.edit_shop_cart_good_success)
        else:
            return Response(response_code.edit_shop_cart_good_error)

    @method_decorator(login_required(login_url='consumer/login/'))
    def delete(self, request):
        """删除商品DELETE请求"""

        user = request.user
        data = request.data

        # 单删
        is_success = self.redis.delete_one_good(user.pk, **data)

        # 群删
        if is_success:
            return Response(response_code.delete_shop_cart_good_success)
        else:
            return Response(response_code.delete_shop_cart_good_error)
