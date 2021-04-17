# -*- coding: utf-8 -*-
# @Time  : 2021/4/6 下午8:31
# @Author : 司云中
# @File : carousel_serializers.py
# @Software: Pycharm



from rest_framework import serializers

from shop_app.models.commodity_models import Carousel


class CarouselSerializer(serializers.ModelSerializer):
    """轮播图显示序列化器"""

    class Meta:
        model = Carousel
        fields = ('url', 'sort', 'type', 'url', 'add_time')




