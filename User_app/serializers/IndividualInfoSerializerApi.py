# -*- coding: utf-8 -*-
# @Time  : 2020/8/4 下午9:00
# @Author : 司云中
# @File : IndividualInfoSerializerApi.py
# @Software: Pycharm
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from User_app.validators import DRFUsernameValidator


class IndividualInfoSerializer(serializers.ModelSerializer):
    """个人信息序列化器"""

    # 覆盖model中的字段效果
    username = serializers.CharField(max_length=30,
                                     validators=[DRFUsernameValidator(), UniqueValidator(queryset=User.objects.all())])

    phone = serializers.CharField(max_length=11, source='consumer.phone', read_only=True)
    head_image = serializers.CharField(source='consumer.head_image', read_only=True)
    birthday = serializers.DateField(source='consumer.birthday', read_only=True)
    sex = serializers.CharField(source='consumer.get_sex_display', read_only=True)
    rank = serializers.CharField(source='consumer.get_rank_display', read_only=True)
    safety = serializers.IntegerField(source='consumer.safety', read_only=True)

    class Meta:
        model = User
        exclude = ['id', 'password', 'last_login', 'last_name', 'is_staff', 'is_active', 'groups', 'user_permissions',
                   'is_superuser']
        # 继承ModelSerializer后，上面定义的自定义字段要显示使用read_only，不能放到read_only_fields中，没有效果
        read_only_fields = ['id', 'password', 'last_login', 'last_name', 'is_staff', 'is_active', 'groups',
                            'user_permissions', 'is_superuser', 'first_name', 'email', 'date_joined'
                            ]
