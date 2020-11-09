# -*- coding: utf-8 -*-
# @Time : 2020/5/5 18:42
# @Author : 司云中
# @File : personal_api.py
# @Software: PyCharm
import datetime
import importlib

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from Emall.loggings import Logging
from Emall.response_code import response_code
from shop_app.models.commodity_models import Commodity
from user_app.model.trolley_models import Trolley
from user_app.models import Address, Collection
from user_app.redis.favorites_redis import favorites_redis
from user_app.redis.foot_redis import FootRedisOperation
from user_app.redis.shopcart_redis import ShopCartRedisOperation
from user_app.redis.user_redis import RedisUserOperation
from user_app.serializers.address_serializers import AddressSerializers
from user_app.serializers.bind_email_phone_serializers import BindPhoneOrEmailSerializer
from user_app.serializers.favorites_serializers import FavoritesSerializer
from user_app.serializers.foot_serializers import FootSerializer
from user_app.serializers.individual_info_serializers import IndividualInfoSerializer, HeadImageSerializer, \
    VerifyIdCardSerializer
from user_app.serializers.password_serializers import PasswordSerializer
from user_app.serializers.shopcart_serializers import ShopCartSerializer
from user_app.signals import add_favorites, delete_favorites
from user_app.utils.pagination import FootResultsSetPagination, FavoritesPagination, TrolleyResultsSetPagination

common_logger = Logging.logger('django')
consumer_logger = Logging.logger('consumer_')

User = get_user_model()


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
        """
        动态导入模块，生成storage实例对象
        :param args:
        :param kwargs:
        :return: instance
        """
        module_path, class_name = self.get_storage_class().rsplit('.', 1)
        storage = getattr(importlib.import_module(module_path), class_name)
        return storage(**kwargs)

    def get_object(self):
        """
        获取消费者对象
        :return: instance
        """
        try:
            return User.objects.get(user=self.request.user)
        except User.DoesNotExist:
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
        return f'find-password-{self.request.user.get_username()}'

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

    @staticmethod
    def bind_phone(cache, instance, validated_data):
        """改绑手机号"""
        is_existed = validated_data['is_existed']
        code = validated_data['code']
        new_phone = validated_data['phone']
        if is_existed:
            # 旧手机接受验证码
            old_phone = validated_data['old_phone']
            is_success = cache.check_code(old_phone, code)
        else:
            # 新手机中核对验证码
            is_success = cache.check_code(new_phone, code)
        if is_success:
            instance.phone = new_phone
            try:
                instance.save()
            except Exception as e:
                consumer_logger.error(e)
                return False
            else:
                return True
        return False

    @staticmethod
    def bind_email(cache, instance, validated_data):
        """改绑邮箱"""
        is_existed = validated_data['is_existed']
        code = validated_data['code']
        new_email = validated_data['email']
        if is_existed:
            # 旧邮箱接受验证码
            old_email = validated_data['old_email']
            is_success = cache.check_code(old_email, code)
        else:
            # 新邮箱中核对验证码
            is_success = cache.check_code(new_email, code)
        if is_success:
            instance.email = new_email
            try:
                instance.save()
            except Exception as e:
                consumer_logger.error(e)
                return False
            else:
                return True
        return False

    def factory(self, way, validated_data, instance):
        """简单工厂管理手机号和邮箱的改绑"""
        func_list = {
            'email': 'bind_email',
            'phone': 'bind_phone',
        }
        func = func_list.get(way)
        bind = getattr(self, func)
        return bind(self.redis, instance, validated_data)

    def put(self, request):
        """改绑OR绑定用户的手机或者邮箱"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 校验成功
        way = serializer.validated_data.get('way')
        bind_success = self.factory(way, serializer.validated_data, request.user)
        # 改绑成功
        if bind_success:
            return Response(response_code.bind_success, status=status.HTTP_200_OK)
        # 改绑失败
        return Response(response_code.bind_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyIdCard(GenericAPIView):
    """OCR身份识别验证"""

    permission_classes = [IsAuthenticated]

    serializer_class = VerifyIdCardSerializer

    def get_object(self):
        """获取inner join的用户对象"""
        return self.request.user  # 如果没有对象在权限会那抛出404

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

    def list(self, request, *args, **kwargs):
        """查看收货地址"""
        # TODO


class FavoriteOperation(GenericViewSet):
    """收藏夹处理"""

    permission_classes = [IsAuthenticated]

    redis = favorites_redis

    serializer_class = FavoritesSerializer  # favorites序列化类

    pagination_class = FavoritesPagination

    def get_queryset(self):
        """
        先hit缓存数据库，如果过期则重新添加到缓存中，否则直接从缓存中取
        :return 结果集/异步任务/空列表 QuerySet/AsyncResult/List
        """
        page_size = FootResultsSetPagination.page_size
        page = self.request.query_params.get(self.pagination_class.page_query_param, 1)  # 默认使用第一页
        resultSet = self.redis.get_resultSet(self.request.user, page=page, page_size=page_size)
        return resultSet

    def get_object(self):
        """
        查找对应pk的收藏夹记录
        :return: Model
        """
        try:
            return Collection.collection_.get(user=self.request.user, pk=self.kwargs.get('pk'))
        except Collection.DoesNotExist:
            raise Http404

    def get_delete_queryset(self):
        """
        欲删除指定用户的所有收藏目录
        :return:结果集合  QuerySet
        """
        return Collection.collection_.filter(user=self.request.user)

    @method_decorator(cache_page(10 * 1, cache='redis'))
    def list(self, request):
        """显示收藏夹的商品"""

        queryset = self.get_queryset()

        if isinstance(queryset, QuerySet):  # 命中数据库
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        queryset = self.get_queryset()
        if isinstance(queryset, QuerySet):  # 命中数据库
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        # if isinstance(queryset, AsyncResult):   # 命中缓存
        #     # 最迟2s获取数据
        #     limit = 2
        #     while not queryset.get() or limit:  # 轮循一直有结果才返回get()
        #         time.sleep(1)
        #         limit -= 1
        #     return Response(queryset.get())
        elif isinstance(queryset, str):  # 命中缓存，读取缓存中的数据
            # 将redis中的序列化数据格式成分页器
            return Response({'data': queryset})
        elif isinstance(queryset, list):  # 缓存为空，数据库也为空，防止缓存击穿
            return Response({'data': queryset})
        else:
            common_logger.info(type(queryset))
            return Response(response_code.verification_code_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_collection(self, type, queryset):
        """
        创建某用户收藏记录
        :param type: 功能类型 'commodity',  str
        :param queryset: {'commodity':QuerySet}, dict
        :return:Bool
        """
        queryset = queryset.get(type)  # 为了可序列化，取QuerySet的第一个元素，反正也只有一个
        try:
            if queryset:
                now = datetime.datetime.now()  # 生产时间戳
                queryset_first = {type: queryset.first()}
                instance = Collection.collection_.create(user=self.request.user, datetime=now, **queryset_first)
                add_favorites.send(  # 发送信号，同步redis
                    sender=Collection,
                    instance=instance,
                    user=self.request.user,
                    queryset=queryset,
                )
                return True if instance else False
            else:
                return False
        except Exception as e:
            consumer_logger.error(e)
            return False

    def create(self, request):
        """添加商品到收藏夹"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        store, commodity = self.get_serializer_class().get_store_commodity(serializer.validated_data)
        is_created = False
        if store:
            is_created = self.create_collection('store', {'store': store})
        elif commodity:
            is_created = self.create_collection('commodity', {'commodity': commodity})
        if is_created:
            return Response(response_code.add_favorites_success)
        else:
            raise Http404

    def destroy(self, request, *args, **kwargs):
        """单删收藏夹商品"""
        obj = self.get_object()
        is_deleted, delete_dict = obj.delete()
        if is_deleted:
            delete_favorites.send(
                sender=Collection,
                user=self.request.user,
                collection_pk=self.kwargs.get('pk'),
                is_all=False
            )
            return Response(response_code.delete_favorites_success)
        else:
            return Response(response_code.delete_favorites_error)

    @action(methods=['delete'], detail=False)
    def destroy_all(self, request):
        """全删收藏夹"""
        queryset = self.get_delete_queryset()
        delete_counts, dict_delete = queryset.delete()
        if delete_counts:
            delete_favorites.send(
                sender=Collection,
                user=self.request.user,
                is_all=True
            )
            return Response(response_code.delete_favorites_success)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)  # 无响应内容，避免显示已删除


class FootOperation(GenericViewSet):
    """浏览足迹处理"""

    # permission_classes = [IsAuthenticated]

    redis = FootRedisOperation.choice_redis_db('redis')

    pagination_class = FootResultsSetPagination

    serializer_class = FootSerializer  # 序列化器

    def get_serializer_context(self):
        return {
            'timestamp': self.get_commodity_dict
        }

    @property
    def get_commodity_dict(self):
        """缓存{commodity_pk:timestamp}"""
        return self.commodity_dict if hasattr(self, 'commodity_dict') else {}

    def get_queryset(self):
        """获取足迹固定数量的商品查询集"""
        page_size = FootResultsSetPagination.page_size
        page = self.request.query_params.get(self.pagination_class.page_query_param, 1)  # 默认使用第一页
        # 按照固定顺序查询固定范围内的商品pk列表
        commodity_dict = self.redis.get_foot_commodity_id_and_page(self.request.user.pk, page=page, page_size=page_size)
        setattr(self, 'commodity_dict', commodity_dict)
        ordering = 'FIELD(`id`,{})'.format(','.join((str(pk) for pk in commodity_dict.keys())))
        return Commodity.commodity_.filter(pk__in=commodity_dict.keys()).extra(select={"ordering": ordering},
                                                                               order_by=(
                                                                                   "ordering",)) if commodity_dict else []

    def create(self, request):
        """单增用户足迹"""
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.redis.add_foot_commodity_id(user.pk, serializer.validated_data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # @method_decorator(cache_page(30, cache='redis'))
    def list(self, request, *args, **kwargs):
        """
        处理某用户固定数量的足迹
        """
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            consumer_logger.error(e)
            return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """删除一条记录"""
        user = request.user
        pk = kwargs.get('pk')
        self.redis.delete_foot_commodity_id(user.pk, commodity_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)  # 删完前端刷新就行了

    @action(methods=['delete'], detail=True)
    def destroy_all(self, request, *args, **kwargs):
        """删除全部记录"""
        user = request.user
        self.redis.delete_foot_commodity_id(user.pk, is_all=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopCartOperation(GenericViewSet):
    """购物车的相关操作"""

    model_class = Trolley

    permission_classes = [IsAuthenticated]

    redis = ShopCartRedisOperation.choice_redis_db('redis')

    serializer_class = ShopCartSerializer  # 序列化器

    pagination_class = TrolleyResultsSetPagination

    def get_model_class(self):
        return self.model_class

    def get_queryset(self):
        return self.get_model_class().trolley_.select_related('commodity', 'store').filter(user=self.request.user)

    def get_delete_queryset(self, pk_list):
        return self.get_model_class().trolley_.filter(user=self.request.user, pk__in=pk_list)

    def list(self, request, *args, **kwargs):
        """显示购物车列表"""

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """单删购物车中的商品"""
        obj = self.get_object()
        row_counts, delete_dict = obj.delete()
        if row_counts:
            return Response(response_code.delete_shop_cart_good_success)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['delete'], detail=False)
    def destroy_many(self, request, *args, **kwargs):
        """群删购物车中的商品"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        queryset = self.get_delete_queryset(serializer.validated_data.get('pk_list'))
        row_counts, delete_dict = queryset.delete()
        if row_counts:
            return Response(response_code.delete_shop_cart_good_success)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        """添加商品到购物车"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_created = serializer.add_trolley(serializer.validated_data)
        if is_created:
            return Response(response_code.add_goods_into_shop_cart_success)
        return Response(response_code.server_error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def context(self, instances, store_commodity_dict, commodity_and_store, commodity_and_price):
    #     return {'instances': instances, 'serializer': self.get_serializer_class,
    #             'context': {'store_and_commodity': store_commodity_dict,
    #                         'commodity_and_store': commodity_and_store,
    #                         'commodity_and_price': commodity_and_price}}

#     @method_decorator(login_required(login_url='consumer/login/'))
#     def get(self, request):
#         """
#         查询购物车相关商品GET请求
#         格式如下：
# {
#     "page": 2,
#     "data": [
#         {
#             "commodity_name": "旺仔牛奶",
#             "grade": "四星好评",
#             "reward_content": "宝贝非常好，质量不错，下次继续买你家的，不过物流太慢了，好几天才到！",
#             "reward_time": "2020-05-29T15:20:53",
#             "price": 5,
#             "category": "食品",
#             "image": null
#         },
#         {
#             "commodity_name": "鹿皮棉袄",
#             "grade": "四星好评",
#             "reward_content": "宝贝非常好，质量不错，下次继续买你家的，不过物流太慢了，好几天才到！",
#             "reward_time": "2020-05-28T15:20:53",
#             "price": 300,
#             "category": "衣服",
#             "image": null
#         },
#     ]
# }
#         """
#
#         try:
#             user = request.user
#             data = request.GET
#             # retrieve information based on dict form and page(int)
#             store_commodity_dict, price_commodity_dict, commodity_counts_dict, page = \
#                 self.redis.get_shop_cart_id_and_page(user.pk, **data)
#             # generate instances of store
#             store_instances = self.get_serializer_class.get_stores(store_commodity_dict.keys())
#             page = Page(page)
#             # 这里序列化器嵌套调用
#             serializer = self.get_ultimate_serializer_class(page,
#                                                             context=self.context(store_instances, store_commodity_dict,
#                                                                                  commodity_counts_dict,
#                                                                                  price_commodity_dict))
#             return Response(serializer.data)
#         except Exception as e:
#             consumer_logger.error(e)
#             return Response(None)
#
#     # @method_decorator(login_required(login_url='consumer/login/'))
#     # def post(self, request):
#     #     """add new goods into shop cart under the account of consumer who send request"""
#     #     pass
#
#     @method_decorator(login_required(login_url='consumer/login/'))
#     def put(self, request):
#         """修改购物车的商品的数量PUT请求"""
#         user = request.user
#         data = request.data
#         is_success = self.redis.edit_one_good(user.pk, **data)
#         if is_success:
#             return Response(response_code.edit_shop_cart_good_success)
#         else:
#             return Response(response_code.edit_shop_cart_good_error)
#
#     @method_decorator(login_required(login_url='consumer/login/'))
#     def delete(self, request):
#         """删除商品DELETE请求"""
#
#         user = request.user
#         data = request.data
#
#         # 单删
#         is_success = self.redis.delete_one_good(user.pk, **data)
#
#         # 群删
#         if is_success:
#             return Response(response_code.delete_shop_cart_good_success)
#         else:
#             return Response(response_code.delete_shop_cart_good_error)
