# -*- coding: utf-8 -*-
# @Time : 2020/5/5 18:42
# @Author : 司云中
# @File : personal_api.py
# @Software: PyCharm
import datetime

from User_app.models.user_models import Address, Consumer
from User_app.redis.favorites_redis import RedisFavoritesOperation
from User_app.redis.foot_redis import FootRedisOperation
from User_app.redis.shopcart_redis import ShopCartRedisOperation
from User_app.serializers.FavoritesSerializersApi import FavoritesSerializer
from User_app.serializers.AddressSerializerApi import AddressSerializers

from User_app.redis.user_redis import RedisVerificationOperation
from User_app.serializers.FootSerializerApi import FootSerializer
from User_app.serializers.PageSerializerApi import Page, PageSerializer
from User_app.serializers.ShopCartSerializerApi import ShopCartSerializer
from User_app.views.ali_card_ocr import Interface_identify
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction, DatabaseError
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from e_mall.loggings import Logging
from e_mall.response_code import response_code
from rest_framework.response import Response
from rest_framework.views import APIView

common_logger = Logging.logger('django')
consumer_logger = Logging.logger('consumer_')


class SaveInformation(APIView):
    """保存信息"""

    @staticmethod
    def save_user(user, username):
        """修改用户昵称"""
        user.username = username
        try:
            user.save(update_fields=['username'])
        except DatabaseError:
            return Response(response_code.server_error)
        else:
            return Response(response_code.user_infor_change_success)

    def post(self, request):
        """处理修改用户信息POST请求"""
        if not request.user.is_authenticated:
            raise Http404
        username = request.data.get('username')
        user = request.user
        return self.save_user(user, username)


class ChangePassword(APIView):
    """
    修改当前用户的密码
    （会自动清除session中的信息，重新登陆）
    """

    @staticmethod
    def modify_password(user, old_password, new_password):
        """改变用户的密码"""
        try:
            is_checked = user.check_password(old_password)  # 核查旧密码
            if not is_checked:
                return Response(response_code.user_original_password_error)
            else:
                user.set_password(new_password)  # 设置新密码
        except User.DoesNotExist:
            return Response(response_code.user_not_existed)
        else:
            try:
                user.save(update_fields=["password"])
            except Exception:
                return Response(response_code.modify_password_verification_error)
            else:
                return Response(response_code.modify_password_verification_success)

    def post(self, request):
        """处理密码修改POST请求"""
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        user = request.user
        return self.modify_password(user, old_password, new_password)


# 来人，给朕废了它
class SetpayPassword(APIView):
    def post(self, request):
        pass


class BindEmailOrPhone(APIView):
    """
    绑定（改绑）用户邮箱或者手机号
    需发送验证码验证
    """
    redis = RedisVerificationOperation.choice_redis_db('redis')  # 选择redis的db

    def bind_email(self, request, user, code):
        """绑定（改绑）手机号"""
        new_email = request.data.get('new_email')
        old_email = request.data.get('old_email')
        is_true = self.redis.check_code(old_email, code)  # 与redis中验证码核对
        if not is_true:
            return Response(response_code.verification_code_error)
        else:
            user.email = new_email
            try:
                user.save(update_fields=['email'])
            except Exception:
                return Response(response_code.server_error)
            else:
                return Response(response_code.bind_email_success)

    def bind_phone(self, request, user, code):
        """绑定（改绑）手机号"""
        new_phone = request.data.get('new_phone')
        old_phone = request.data.get('old_phone')
        is_true = self.redis.check_code(old_phone, code)  # 核对验证码
        if not is_true:
            return Response(response_code.verification_code_error)
        else:
            consumer = Consumer.consumer_.get(user=user)
            consumer.phone = new_phone
            try:
                with transaction.atomic():
                    consumer.save(update_fileds=['phone'])
            except DatabaseError:
                return Response(response_code.server_error)
            else:
                return Response(response_code.bind_phone_success)

    def factory(self, request, user, code, way):
        """简单工厂管理手机号和邮箱的改绑"""
        func_list = {
            'email': 'bind_email',
            'phone': 'bind_phone',
        }
        func = func_list.get(way)
        result = getattr(self, func)
        return result(request, user, code)

    def post(self, request):
        """处理改绑POST请求"""
        way = request.data.get('way')
        code = request.data.get('code')
        user = request.user
        return self.factory(request, user, code, way)


class VerifyIdCard(APIView):
    """OCR识别验证"""

    @staticmethod
    def trans_sex(read_sex):
        """ 转换性别 """
        if read_sex == '男':
            return 'm'
        elif read_sex == '女':
            return 'f'

    @staticmethod
    def trans_birth(read_birth):
        """重构生日"""
        year = read_birth[0:4]
        month = read_birth[4:6]
        day = read_birth[6:8]
        birth_str = '%(year)s-%(month)s-%(day)s' % ({'year': year, 'month': month, 'day': day})
        birthday = datetime.datetime.strptime(birth_str, '%Y-%m-%d')
        return birthday

    def verify(self, pk, image, card_type):
        """阿里OCR识别身份证"""
        user = User.objects.get(pk=pk)  # inner join
        identify_instance = Interface_identify(image, card_type)  # 返回识别实例

        if not identify_instance.is_success:  # 判断是否识别成功
            return Response(response_code.real_name_authentication_error)
        else:
            user.first_name = identify_instance.get_detail('actual_name')
            sex = identify_instance.get_detail('sex')
            birth = identify_instance.get_detail('birth')
            user.consumer.sex = self.trans_sex(sex)
            user.consumer.birthday = self.trans_birth(birth)
        try:
            with transaction.atomic():
                # 开启事务，原子修改
                user.consumer.save(update_fields=['sex', 'birthday'])
                user.save(update_fields=['first_name'])
        except DatabaseError:
            return Response(response_code.server_error)
        else:
            return Response(response_code.real_name_authentication_success)

    def post(self, request):
        """处理POST请求"""
        pk = request.user.pk
        image = request.data.get('image')
        card_type = request.data.get('card_type')
        # both image.file.read() and image.read() is efficient to get type of binary
        return self.verify(pk, image.file.read(), card_type)


class SecretSecurity(APIView):
    """来人，把它拖出去给我斩了"""
    pass


class AddressOperation(APIView):
    """
    收货地址处理（之后重构以下，改继承APIView的工具类）
    """

    @staticmethod
    def add_new_address(user, data):
        """增加新地址"""
        serializer = AddressSerializers(data=data)
        if serializer.is_valid():
            # 会调用各字段的validators验证器
            # 传入data数据实例化serializer对象，才可以调用is_valid()方法，才能校验获取validated_data
            is_true = serializer.add_or_edit_address(user, data)
            if is_true:
                return Response(response_code.address_add_success)
            else:
                return Response(response_code.address_add_error)
        return Response(serializer.errors)

    @staticmethod
    def put_default_address(user, data):
        """修改默认地址"""
        try:
            with transaction.atomic():
                addresses = Address.address_.filter(user=user)
                addresses.filter(default_address=True).update(default_address=False)  # 全置为False
                addresses.filter(pk=data.get('pk')).update(default_address=True)     # 重设默认地址
        except DatabaseError:
            return Response(response_code.modify_default_error)
        else:
            return Response(response_code.modify_default_success)

    @staticmethod
    def put_edit_address(user, data):
        """修改地址"""
        serializer = AddressSerializers(data=data)
        if serializer.is_valid():
            is_true = serializer.add_or_edit_address(user, data)
            if is_true:
                return Response(response_code.address_edit_success)
            else:
                return Response(response_code.address_edit_error)
        # 以后改成server_error
        return Response(serializer.errors)

    @staticmethod
    def delete_address(user, data):
        """删除某个选定的地址"""
        try:
            with transaction.atomic():
                Address.address_.get(pk=data.get('pk')).delete()
        except DatabaseError as e:
            common_logger.info(e)
            return Response(response_code.delete_address_error)
        else:
            return Response(response_code.delete_address_success)

    def factory(self, user, way, data):
        """简单工厂管理地址处理操作"""
        func_dict = {
            'default': 'put_default_address',
            'edit': 'put_edit_address',
            'add': 'add_new_address',
            'delete': 'delete_address',
        }
        func = func_dict.get(way)
        result = getattr(self, func)
        return result(user, data)

    @method_decorator(login_required(login_url='consumer/login/'))
    def put(self, request):
        """修改地址PUT请求"""
        data = request.data.copy()
        way = data.pop('way')[0]
        user = request.user
        common_logger.info(data)
        return self.factory(user, way, data)

    @method_decorator(login_required(login_url='consumer/login/'))
    def post(self, request):
        """增加地址POST请求"""
        data = request.data.copy()
        way = data.pop('way')[0]
        user = request.user
        return self.factory(user, way, data)

    @method_decorator(login_required(login_url='consumer/login/'))
    def delete(self, request):
        """删除地址DELETE请求"""
        data = request.data.copy()
        common_logger.info(data)
        way = data.pop('way')[0]
        user = request.user
        return self.factory(user, way, data)


class FavoriteOperation(APIView):
    """
    收藏夹处理
    """
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
