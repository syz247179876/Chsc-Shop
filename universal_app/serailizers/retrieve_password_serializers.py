# -*- coding: utf-8 -*-
# @Time  : 2020/10/13 下午7:47
# @Author : 司云中
# @File : retrieve_password_serializers.py
# @Software: Pycharm
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.db.models.query import QuerySet
from rest_framework import serializers
from django.utils.translation import ugettext as _
import uuid

from django.contrib.auth import get_user_model

User = get_user_model()

def generate_proof():
    """生成唯一凭证"""
    return uuid.uuid1()


def retrieve_mac(self):
    """拿去客户端的mac地址"""
    return self.context.get('request').GET.get('mac')


def retrieve_redis(self):
    return self.context.get('redis')


def retrieve_ip(self):
    """获取客户端的ip地址"""
    request = self.context.get('request')
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # 这里是真实的ip
    else:
        ip = request.META.get('REMOTE_ADDR')  # 这里获得代理ip,如果没有代理也是真实IP
    return ip


class RetrievePasswordSerializer(serializers.Serializer):
    """找回密码序列化器"""

    RETRIEVE_KEY = 'retrieve_key'

    RETRIEVE_WAY = (
        ('email', 'email'),
        ('phone', 'phone'),
    )


    def __init__(self):
        super().__init__()

        self.fields[self.RETRIEVE_KEY] = serializers.CharField(max_length=30, validators=[])
        self.fields['code'] = serializers.CharField(max_length=6)
        self.fields['way'] = serializers.ChoiceField(choices=self.RETRIEVE_WAY)


    def validate(self, attrs):
        redis = retrieve_redis(self)
        key = redis.key('retrieve-pwd', attrs.get('way'), attrs.get(self.RETRIEVE_KEY))
        if redis.check_code(key, attrs.get('code')):
            # 验证码正确,生成修改密码唯一凭证,10分钟
            key = redis.key(self.RETRIEVE_KEY, retrieve_ip(self), retrieve_mac(self))
            redis.save_code(key, generate_proof(), 600)
            return attrs
        raise serializers.ValidationError('验证码错误')




class NewPasswordSerializer(serializers.Serializer):
    """重置密码序列化器"""

    RETRIEVE_KEY = 'retrieve_key'

    first_password = serializers.CharField(max_length=20,min_length=8)
    second_password = serializers.CharField(max_length=20,min_length=8)


    @property
    def key(self):
        """生成访问唯一redis的唯一凭证"""
        request = self.context.get('request')
        redis = retrieve_redis(self)
        return redis.save_code(request.GET.get('way'), request.GET.get(self.RETRIEVE_KEY), request.GET.get('mac'), retrieve_ip(self))

    def validate_first_password(self, value):

        request = self.context.get('request')
        retrieve_key = request.GET.get(self.RETRIEVE_KEY)
        hash_pwd = make_password(value)
        way = request.GET.get('way')
        if way not in ['email', 'phone']:
            # 限制way必须在email,phone二选一
            raise serializers.ValidationError('校验方式异常')
        query_dict = {way:retrieve_key}
        try:
            if hash_pwd == User.objects.get(**query_dict).password:
                # 如果旧密码和当前修改的密码一样,告诉用户
                raise serializers.ValidationError('密码不能与旧密码重复')
        except User.DoesNotExist:
            raise serializers.ValidationError('当前用户不存在')


    def validate(self, attrs):
        first_password = attrs.get('first_password')
        second_password = attrs.get('first_password')

        if first_password != second_password:
            raise serializers.ValidationError('新旧密码不一致')

        # 验证唯一凭证
        redis = retrieve_redis(self)
        is_check, identity = redis.check_code_retrieve(self.key)

        if is_check:
            attrs.update({'identity': identity, 'way':self.context.get('request').GET.get(self.RETRIEVE_KEY)})
            return attrs
        else:
            raise serializers.ValidationError('凭证无效,客户端与服务器不匹配!')


    def update_password(self,validated_data):
        """更新旧密码"""
        first_password = validated_data.pop('first_password')
        retrieve_key = validated_data.pop(self.RETRIEVE_KEY)
        way = validated_data.pop('way')
        query_dict = {way:retrieve_key}
        # 更新新密码
        updated_rows = User.objects.filter(**query_dict).update(password=make_password(first_password))
        return True if updated_rows else False








