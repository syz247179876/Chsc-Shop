# -*- coding: utf-8 -*- 
# @Time : 2020/5/29 19:53 
# @Author : 司云中 
# @File : PageSerializerApi.py 
# @Software: PyCharm

from e_mall.loggings import Logging
from rest_framework import serializers
from rest_framework.request import Empty


common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class PageSerializer(serializers.Serializer):
    """页数序列器"""

    page = serializers.IntegerField()

    data = serializers.SerializerMethodField()

    @property
    def serializer_class(self):
        """获取context传过来的序列化器"""
        return self.context.get('serializer')

    def get_data(self, obj):
        """additional serializer"""
        instances = self.context.get('instances', None)
        context = self.context.get('context', {})
        # data = self.context.get('data', Empty)
        return self.serializer_class(instances, context=context, many=True).data


class Page:
    """页数"""

    def __init__(self, page):
        self.page = page
