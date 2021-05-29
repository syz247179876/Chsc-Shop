# -*- coding: utf-8 -*-
# @Time  : 2021/2/18 下午5:54
# @Author : 司云中
# @File : urls.py
# @Software: Pycharm
from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter

from seller_app.apis.seller_commodity_api import SellerCommodityApiView, SkuPropApiView, FreightApiView, \
    SellerSkuApiView, FreightItemApiView, SellerCommodityExtraApiView
from seller_app.apis.seller_menu_api import SellerMenuApiView
from seller_app.apis.seller_store_api import SellerStoreApiView, SellerInfoApiView

app_name = 'seller_app'

urlpatterns = [
    path(f'{settings.URL_PREFIX}/commodity/',SellerCommodityApiView.as_view()),
    path(f'{settings.URL_PREFIX}/sku-property/', SkuPropApiView.as_view()),
    path(f'{settings.URL_PREFIX}/store/', SellerStoreApiView.as_view()),
    path(f'{settings.URL_PREFIX}/freight/', FreightApiView.as_view()),
    path(f'{settings.URL_PREFIX}/sku/', SellerSkuApiView.as_view()),
    path(f'{settings.URL_PREFIX}/menu/', SellerMenuApiView.as_view())
]

router = DefaultRouter()
router.register(f'{settings.URL_PREFIX}/info', SellerInfoApiView, basename='info')
router.register(f'{settings.URL_PREFIX}/freight-item', FreightItemApiView, basename='freight-item')
router.register(f'{settings.URL_PREFIX}/commodity-extra', SellerCommodityExtraApiView, basename='commodity-extra')
urlpatterns += router.urls