# -*- coding: utf-8 -*- 
# @Time : 2020/5/29 14:09 
# @Author : 司云中 
# @File : remark_api.py 
# @Software: PyCharm
from Remark_app.serializers.UserMarkerSerializerApi import UserMarkerSerializer, PageSerializer, Page
from e_mall.loggings import Logging
from rest_framework.response import Response
from rest_framework.views import APIView

common_logger = Logging.logger('django')

evaluate_logger = Logging.logger('evaluate_')


class RemarkOperation(APIView):
    serializer_class = UserMarkerSerializer

    ultimate_class = PageSerializer

    def context(self, instances):
        """extra parameters"""
        return {
            'instances': instances,
            'serializer': self.get_serializer_class
        }

    @property
    def get_ultimate_serializer_class(self):
        return self.ultimate_class

    @property
    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class
        return serializer_class(*args, **kwargs)

    def get_ultimate_serializer(self, *args, **kwargs):
        serializer_class = self.get_ultimate_serializer_class
        return serializer_class(*args, **kwargs)

    def get_remark_and_page(self, user, **kwargs):
        """
        get limit instance(querysets) of models
        :param user: 当前登录的用户
        :param kwargs: 额外参数，包括limit和page
        :return: queryset
        """
        return self.get_serializer_class.get_remark_and_page(user, **kwargs)

    def get(self, request):
        user = request.user
        data = request.GET
        instances, page = self.get_remark_and_page(user, **data)
        page = Page(page)
        serializer = self.get_ultimate_serializer(page, context=self.context(instances))
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        data = request.data
        pass

    def delete(self, request):
        user = request.user
        data = request.data
        pass
