# -*- coding: utf-8 -*-
# @Time  : 2020/8/30 下午4:32
# @Author : 司云中
# @File : attitude_action_serializers.py
# @Software: Pycharm

from rest_framework import serializers

from remark_app.models.remark_models import Remark
from remark_app.signals import praise_or_against_post, praise_or_against_cancel, check_remark_action


class AttitudeRemarkSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(write_only=True)

    p_or_n = serializers.BooleanField(write_only=True)  # 点赞还是差评

    status = serializers.BooleanField(write_only=True)  # 执行/取消操作,执行：True，取消：False

    def validate_commodity(self, value):
        if value <= 0:
            raise serializers.ValidationError('参数数值异常')
        return value

    def validate(self, attrs):
        """验证当前用户是否已经点赞/反对"""
        result = check_remark_action.send(
            sender=Remark,
            pk=attrs.get('pk'),
            user=self.context.get('request').user,
            is_remark=False,
            is_action=True
        )
        if result[0][1] == True and attrs.get('status') == True:  # 执行与当前状态相反,则已经点赞/反对，反之未点赞/反对
            raise serializers.ValidationError('您已经点赞/反对了')
        elif result[0][1] == False and attrs.get('status') == False:
            raise serializers.ValidationError('您还未点赞/反对')
        else:
            return attrs

    def add_action(self, obj):
        """更新点赞/反对量"""
        p_or_n = self.validated_data['p_or_n']
        if p_or_n:
            obj.praise += 1
        else:
            obj.against += 1
        obj.is_action = True
        obj.save(update_fields=['praise', 'against', 'is_action'])
        praise_or_against_post.send(
            sender=type(self),
            pk=self.validated_data['pk'],   # 评论/回复的pk
            user=self.context.get('request').user
        )
        return obj

    def cancel_action(self, obj):
        """取消点赞/反对"""
        p_or_n = self.validated_data['p_or_n']
        if p_or_n:
            obj.praise -= 1
        else:
            obj.against -= 1
        obj.is_action = False
        obj.save(update_fields=['praise', 'against', 'is_action'])
        praise_or_against_cancel.send(
            sender=type(self),
            pk=self.validated_data['pk'],
            user=self.context.get('request').user
        )
        return obj

    def execute_action(self, obj):
        if self.validated_data.get('status'):
            obj = self.add_action(obj)
        else:
            obj = self.cancel_action(obj)
        return obj

    class Meta:
        model = Remark
        fields = ('praise', 'against', 'is_remark', 'pk', 'p_or_n', 'status')
        read_only_fields = (
              'is_remark', 'praise', 'against'
        )


# class AttitudeReplySerializer(serializers.ModelSerializer):
#
#     pk = serializers.IntegerField(write_only=True)
#
#     p_or_n = serializers.BooleanField(write_only=True)  # 点赞还是差评
#
#     status = serializers.BooleanField(write_only=True)  # 执行/取消操作,执行：True，取消：False
#
#     def validate_commodity(self, value):
#         if value <= 0:
#             raise serializers.ValidationError('参数数值异常')
#         return value
#
#     def validate(self, attr):
#         """验证当前用户是否已经点赞/反对"""
#         result = check_remark_action.send(
#                 sender=self.Meta.model,
#                 user=self.context.get('request').get('user')
#         )
#         if result[0][1] == attr.get('status'):  # 执行与当前状态相反,则已经点赞/反对，反之未点赞/反对
#             raise serializers.ValidationError('您已经点赞/反对了')
#         else:
#             return attr
#
#
#     class Meta:
#         model = RemarkReply
#         fields = ('praise', 'against', 'is_remark')
#         read_only_fields = (
#             'is_remark', 'praise', 'against'
#         )
