from rest_framework import routers

from Shop_app.views.shop import enter_introduction_page
from Shop_app.views.shop_api import AddShopCartOperation, AddFavoritesOperation, CommoditySearchOperation
from django.urls import path, include

app_name = 'Shop_app'

urlpatterns = [
    path('introduce/<int:pk>', enter_introduction_page, name='introduce'),
    path('add-into-shop-cart/', AddShopCartOperation.as_view(), name='add-into-shop-cart'),
    path('add-into-favorites-chsc-api/', AddFavoritesOperation.as_view(), name='add-into-favorites-chsc-api'),
    path('shop-chsc-search/', CommoditySearchOperation.as_view(), name='shop-chsc-search')
]

# DRF视图集注册
# router = routers.DefaultRouter()
# router.register('api/shop-chsc-search', CommoditySearchOperation, base_name="shop_chsc_search")
# urlpatterns += router.urls
