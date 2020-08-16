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


class HeadImageSerializer(serializers.Serializer):
    """头像修改序列化器"""

    head_image = serializers.ImageField(write_only=True)

    @staticmethod
    def _upload(validated_data, storage):
        """上传用户新的头像"""
        head_image = validated_data.get('head_image')
        is_upload, file_information = storage.upload(filebuffer=head_image.read())  # 调用client进行文件上传
        return is_upload

    @staticmethod
    def _update(validated_data, remote_file_id, storage):
        """
        存在问题！！！
        更新用户头像，
        在用户保存头像后
        """
        head_image = validated_data.get('head_image')
        is_update, file_information = storage.update(bytes(head_image.read()), remote_file_id)
        return is_update

    def update_head_image(self, instance, validated_data, storage):
        try:
            head_image = instance.head_image
            is_upload = self._upload(validated_data, storage)
            consumer = instance.save(update_fields=['head_image', ])
        except Exception as e:
            return False
        else:
            is_delete = storage.delete(head_image)
            return True if all([consumer,is_upload,is_delete]) else False  # 只有上传+修改+删除（可选）都成功后才返回True
        # return self._update(validated_data, 'group1/M00/00/00/wKgAaV85MnSAKwl7AA543lGjCZc0505542', storage)
