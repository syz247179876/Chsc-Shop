# -*- coding: utf-8 -*-
# @Time  : 2020/8/4 下午5:32
# @Author : 司云中
# @File : SecKillSerializerApi.py
# @Software: Pycharm


from rest_framework import serializers


class SecKillSerializer(serializers.Serializer):
    """
    秒杀序列化器
    生成订单并加锁，完成交易解锁
    DRF限流
    """
    pass








