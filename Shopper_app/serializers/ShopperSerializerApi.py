# -*- coding: utf-8 -*- 
# @Time : 2020/6/1 23:26 
# @Author : 司云中 
# @File : ShopperSerializerApi.py 
# @Software: PyCharm

from django.contrib.auth.models import User
from django.db import transaction, DatabaseError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from Shopper_app.models.shopper_models import Shoppers, Store
from Shopper_app.validators import DRFPhoneValidator, DRFStoreNameValidator
from User_app.views.ali_card_ocr import Interface_identify
from e_mall.loggings import Logging

common_logger = Logging.logger('django')

shopper_logger = Logging.logger('shopper_')


class ShopperSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', validators=[UniqueValidator(queryset=User.objects.all())])
    face = serializers.ImageField(max_length=50, allow_empty_file=False)  # 身份证前照
    back = serializers.ImageField(max_length=50, allow_empty_file=False)  # 身份正后照片
    code = serializers.CharField(max_length=6)  # 验证码
    email = serializers.EmailField(required=False, source='user.email',
                                   validators=[UniqueValidator(queryset=User.objects.all())],
                                   )
    phone = serializers.CharField(validators=[DRFPhoneValidator(), UniqueValidator(queryset=Shoppers.shopper_.all())])
    sell_category = serializers.CharField()  # 销售主类
    store_name = serializers.CharField(max_length=30, validators=[DRFStoreNameValidator()])  # 店铺名字
    province = serializers.CharField()
    city = serializers.CharField()

    def validate_code(self, value):
        """验证码校验"""
        if len(value) != 6:
            raise serializers.ValidationError("验证码长度为6位")
        return value

    def validate(self, attrs):
        """
        OCR识别身份正反
        验证阶段验证身份信息是否正确或是否已被验证
        """
        identify_instance_face = Interface_identify(attrs.get('face'), 'face')
        identify_instance_back = Interface_identify(attrs.get('back'), 'back')
        is_success = identify_instance_face.is_success and identify_instance_back.is_success  # 检查身份验证是否全部正确
        if is_success:
            OCR_attrs = {
                'first_name': identify_instance_face.get_detail('actual_name'),
                'sex': identify_instance_face.get_detail('sex'),
                'birthday': identify_instance_face.get_detail('birth'),
                'nationality': identify_instance_face.get_detail('nationality')
            }
            if User.objects.filter(first_name=identify_instance_face.get_detail('actual_name')).count() == 1:
                raise serializers.ValidationError('身份已被认证过！')
            else:
                attrs.update(OCR_attrs)
                return attrs
        raise serializers.ValidationError('身份校验异常')

    @staticmethod
    def create_user(validated_data):
        """创建User用户"""
        username = validated_data['user']['username']
        first_name = validated_data['first_name']
        email = validated_data.get('user').get('email', '')
        user = User.objects.create(username=username, first_name=first_name, is_staff=True, email=email)
        return user

    @staticmethod
    def create_shopper(user, validated_data):
        """创建shopper用户"""
        sex = validated_data['sex']
        phone = validated_data['phone']
        head_image = validated_data.get('head_image', None)
        sell_category = validated_data['sell_category']
        shopper = Shoppers.shopper_.create(user=user, sex=sex, phone=phone, head_image=head_image,
                                           sell_category=sell_category)
        return shopper

    @staticmethod
    def create_store(user, validated_data):
        """创建店铺"""
        store_name = validated_data['store_name']
        province = validated_data['province']
        city = validated_data['city']
        store = Store.store_.create(shopper=user, store_name=store_name, province=province, city=city)
        return store

    def create(self, validated_data):
        """创建汇总"""
        try:
            with transaction.atomic():  # 开启事务
                user = self.create_user(validated_data)
                self.create_shopper(user, validated_data)
                self.create_store(user, validated_data)
        except Exception as e:
            shopper_logger.error(e)
            return None
        return user

    class Meta:
        model = Shoppers
        exclude = ['user', 'credit']
