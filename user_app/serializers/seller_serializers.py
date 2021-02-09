# # -*- coding: utf-8 -*-
# # @Time : 2020/6/1 23:26
# # @Author : 司云中
# # @File : seller_serializers.py
# # @Software: PyCharm
#
# from user_app.models import User
# from django.db import transaction
# from rest_framework import serializers
# from rest_framework.validators import UniqueValidator
# from rest_framework_jwt.compat import PasswordField
# from rest_framework_jwt.settings import api_settings
#
# from user_app.model.seller_models import Shoppers, Store
# from user_app.utils.validators import DRFPhoneValidator
# from Emall.authentication import email_or_username, phone
# from Emall.loggings import Logging
# from django.utils.translation import gettext_lazy as _
#
# from user_app.tasks import ocr
#
# common_logger = Logging.logger('django')
#
# shopper_logger = Logging.logger('shopper_')
#
# jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
# jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
# jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
# jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER
#
#
# class SellerRegisterSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(source='user.username', validators=[UniqueValidator(queryset=User.objects.all())])
#     face = serializers.ImageField(max_length=50, allow_empty_file=False)  # 身份证前照
#     back = serializers.ImageField(max_length=50, allow_empty_file=False)  # 身份正后照片
#     code = serializers.CharField(max_length=6)  # 验证码
#     email = serializers.EmailField(required=False, source='user.email',
#                                    validators=[UniqueValidator(queryset=User.objects.all())],
#                                    )
#     phone = serializers.CharField(validators=[DRFPhoneValidator(), UniqueValidator(queryset=Shoppers.shopper_.all())])
#     sell_category = serializers.CharField()  # 销售主类
#     store_name = serializers.CharField(max_length=30, validators=[])  # 店铺名字
#     province = serializers.CharField()
#     city = serializers.CharField()
#
#     @property
#     def redis(self):
#         """获取redis实例"""
#         return self.context.get('redis')
#
#     def validate_code(self, value):
#         """验证码校验"""
#         if len(value) != 6:
#             raise serializers.ValidationError("验证码为6位数")
#         return value
#
#     def check_code(self, phone, code):
#         return self.redis.check_code(phone, code)
#
#     def validate(self, attrs):
#         """
#         OCR识别身份正反
#         验证阶段验证身份信息是否正确或是否已被验证
#         """
#
#         # 校验验证码
#         if not self.redis.check_code(attrs.get('phone'), attrs.get('code')):
#             raise serializers.ValidationError('验证码错误')
#
#         # 身份校验
#         identify_instance_face = ocr.apply_async(args=(attrs.get('face'), 'face'))  # 扔到任务队列中调度
#         identify_instance_back = ocr.apply_async(args=(attrs.get('back'), 'face'))
#         is_success = identify_instance_face.get() and identify_instance_back.get()  # 检查身份验证是否全部正确
#         if is_success:
#             OCR_attrs = {
#                 'first_name': identify_instance_face.get_detail('actual_name'),
#                 'sex': identify_instance_face.get_detail('sex'),
#                 'birthday': identify_instance_face.get_detail('birth'),
#                 'nationality': identify_instance_face.get_detail('nationality')
#             }
#             if User.objects.filter(first_name=identify_instance_face.get_detail('actual_name')).count() == 1:
#                 raise serializers.ValidationError('身份证已被认证过！')
#             else:
#                 attrs.update(OCR_attrs)
#                 return attrs
#         raise serializers.ValidationError('身份校验异常')
#
#     @staticmethod
#     def create_user(validated_data):
#         """创建User用户"""
#         username = validated_data['user']['username']
#         first_name = validated_data['first_name']
#         email = validated_data.get('user').get('email', '')
#         user = User.objects.create(username=username, first_name=first_name, is_staff=True, email=email)
#         return user
#
#     @staticmethod
#     def create_shopper(user, validated_data):
#         """创建shopper用户"""
#         sex = validated_data['sex']
#         phone = validated_data['phone']
#         head_image = validated_data.get('head_image', None)
#         sell_category = validated_data['sell_category']
#         shopper = Shoppers.shopper_.create(user=user, sex=sex, phone=phone, head_image=head_image,
#                                            sell_category=sell_category)
#         return shopper
#
#     @staticmethod
#     def create_store(user, validated_data):
#         """创建店铺"""
#         store_name = validated_data['store_name']
#         province = validated_data['province']
#         city = validated_data['city']
#         store = Store.store_.create(shopper=user, store_name=store_name, province=province, city=city)
#         return store
#
#     def create(self, validated_data):
#         """创建汇总"""
#         try:
#             with transaction.atomic():  # 开启事务
#                 user = self.create_user(validated_data)
#                 self.create_shopper(user, validated_data)
#                 self.create_store(user, validated_data)
#         except Exception as e:
#             shopper_logger.error(e)
#             return None
#         return user
#
#     class Meta:
#         model = Shoppers
#         exclude = ['user', 'credit']
#
#
# class SellerJwtLoginSerializer(serializers.Serializer):
#     """商家注册序列化器"""
#
#     LOGIN_KEY = 'login_key'
#
#     LOGIN_WAY = (
#         ('username', 'username'),
#         ('email', 'email'),
#         ('phone', 'phone')
#     )
#
#     def __init__(self):
#         """初始化"""
#         super().__init__()
#         self.fields[self.LOGIN_KEY] = serializers.CharField(max_length=30, validators=[])
#         self.fields['code'] = serializers.CharField(max_length=6, required=False)  # 验证码
#         self.fields['password'] = PasswordField(write_only=True, required=False)
#         self.fields['way'] = serializers.ChoiceField(choices=self.LOGIN_WAY)
#
#     def validate(self, attrs):
#         """验证数据,生成token"""
#
#         global user
#
#         # 手机校验验证码
#         if attrs.get('way') == 'phone' and not self.redis.check_code(attrs.get(self.LOGIN_KEY), attrs.get('code')):
#             raise serializers.ValidationError('验证码不存在或错误')
#
#         credentials = {
#             attrs.get('way'): attrs.get(self.LOGIN_KEY),
#             'code': attrs.get('code', 1),
#             'password': attrs.get('password', 1),
#             'way': attrs.get('way')
#         }
#
#         if all(credentials.values()):
#             if credentials.get('way') == 'username':
#                 user = email_or_username.authenticate(**credentials)
#             elif credentials.get('way') == 'email':
#                 user = email_or_username.authenticate(**credentials)
#             elif credentials.get('way') == 'phone':
#                 user = phone.authenticate(**credentials)
#             if user:
#                 if not user.is_active:
#                     msg = _('User account is disabled.')
#                     raise serializers.ValidationError(msg)
#
#                 # 编码形成jwt第二部分
#                 payload = jwt_payload_handler(user)
#
#                 return {
#                     'token': jwt_encode_handler(payload),  # 加密生成token
#                     'user': user,
#                 }
#             else:
#                 msg = _('Unable to log in with provided credentials.')
#                 raise serializers.ValidationError(msg)
#         else:
#             msg = _('Must include "{username_field}","code" and "way".')
#             msg = msg.format(username_field=self.LOGIN_KEY)
#             raise serializers.ValidationError(msg)
#
#     @property
#     def redis(self):
#         """获取视图实例"""
#         return self.context.get('redis')
#
#     def validate_code(self, value):
#         """验证码校验"""
#         if len(value) != 6:
#             raise serializers.ValidationError("验证码为6位数")
#         return value
