# -*- coding: utf-8 -*- 
# @Time : 2020/6/1 17:18 
# @Author : 司云中 
# @File : home_api.py 
# @Software: PyCharm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from e_mall.loggings import Logging
from mainsite.serializers.HomeSerializerApi import GoodsSerializerApi
from mainsite.serializers.PageSerializerApi import PageSerializer, Page
from rest_framework.response import Response
from rest_framework.views import APIView

common_logger = Logging.logger('django')

mainsite_logger = Logging.logger('mainsite_')


class GoodsHomeOperation(APIView):
    """首页商品显示"""
    serializer_class = GoodsSerializerApi

    ultimate_class = PageSerializer

    def context(self, instances):
        return {'instances': instances, 'serializer': self.get_serializer_class}

    @property
    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class
        return serializer_class(*args, **kwargs)

    @property
    def get_ultimate_serializer_class(self):
        return self.ultimate_class

    def get_ultimate_serializer(self, *args, **kwargs):
        serializer = self.get_ultimate_serializer_class
        return serializer(*args, **kwargs)

    def get(self, request):
        """流加载的方式显示数据"""
        try:
            data = request.GET
            # 获取固定数量的商品和最大页数(需动态计算），以便实时更新新上架的商品
            instances, pages = self.get_serializer_class.get_limit_goods(**data)
            page = Page(pages)
            serializer = self.get_ultimate_serializer(page, context=self.context(instances))
            return Response(serializer.data)
        except Exception as e:
            mainsite_logger.error(e)
            return Response(None)


class AddressHomeOperation(APIView):
    """主页显示默认的收获地址"""
    pass
