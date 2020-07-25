# -*- coding: utf-8 -*- 
# @Time : 2020/6/1 23:26 
# @Author : 司云中 
# @File : ShopperSerializerApi.py 
# @Software: PyCharm
import datetime

from Shopper_app.models.shopper_models import Shoppers, Store
from User_app.views.ali_card_ocr import Interface_identify
from django.contrib.auth.models import User
from django.db import transaction, DatabaseError
from e_mall.loggings import Logging
from pymongo.database import Database
from rest_framework import serializers

common_logger = Logging.logger('django')

shopper_logger = Logging.logger('shopper_')


class ShopperSerializer(serializers.ModelSerializer):

    @staticmethod
    def trans_sex(read_sex):
        if read_sex == '男':
            return 'm'
        elif read_sex == '女':
            return 'f'

    @staticmethod
    def trans_birth(read_birth):
        year = read_birth[0:4]
        month = read_birth[4:6]
        day = read_birth[6:8]
        birth_str = '%(year)s-%(month)s-%(day)s' % ({'year': year, 'month': month, 'day': day})
        birthday = datetime.datetime.strptime(birth_str, '%Y-%m-%d')
        return birthday

    @classmethod
    def create_shopper(cls, verified_instance, **data):
        user_name = data.get('user_name')[0]
        user_password = data.get('user_password')[0]
        user_email = data.get('user_email')[0]
        user_phone = data.get('user_phone')[0]
        first_name = verified_instance.get_detail('actual_name')
        sex = cls.trans_sex(verified_instance.get_detail('sex'))
        birthday = cls.trans_birth(verified_instance.get_detail('birth'))
        province = verified_instance.get_detail('address').split('省')[0] + '省'
        try:
            with transaction.atomic():
                user = User.objects.create_shopper(user_name, user_email, user_password, first_name=first_name)
                shopper = Shoppers.shopper_.create(user=user, phone=user_phone, sex=sex, birthday=birthday)
                store = Store.store_.create(store_name=user_name + '的店铺', shopper=user, province=province)
        except DatabaseError as e:
            return None
        except Exception as e:
            shopper_logger.error(e)
            return None
        else:
            return user

    @staticmethod
    def check_shopper_existed(email, phone):
        """check whether the shopper is registered"""

        # 这里后期需要优化，看用户名是否需要不重复
        try:
            user_is_existed = User.objects.filter(email=email).count() == 1
            shopper_is_existed = Shoppers.shopper_.filter(phone=phone).count() == 1
            if user_is_existed:
                return 'email_existed'
            if shopper_is_existed:
                return 'phone_existed'
        except Exception as e:
            shopper_logger.error(e)
            return None
        else:
            return 'not_existed'

    class Meta:
        model = Shoppers
        fields = '__all__'
