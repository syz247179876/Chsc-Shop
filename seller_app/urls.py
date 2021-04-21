# -*- coding: utf-8 -*-
# @Time  : 2021/2/18 下午5:54
# @Author : 司云中
# @File : urls.py
# @Software: Pycharm
from django.conf import settings
from django.urls import path, include

from seller_app.apis.seller_commodity_api import SellerCommodityApiView, SkuPropApiView, FreightApiView, \
    SellerSkuApiView
from seller_app.apis.seller_store_api import SellerStoreApiView

app_name = 'seller_app'

urlpatterns = [
    path(f'{settings.URL_PREFIX}/commodity/',SellerCommodityApiView.as_view() ),
    path(f'{settings.URL_PREFIX}/sku-property/', SkuPropApiView.as_view()),
    path(f'{settings.URL_PREFIX}/store/', SellerStoreApiView.as_view()),
    path(f'{settings.URL_PREFIX}/freight/', FreightApiView.as_view()),
    path(f'{settings.URL_PREFIX}/sku/', SellerSkuApiView.as_view())
]