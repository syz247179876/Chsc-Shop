from rest_framework import routers

from shop_app.apis.shop import enter_introduction_page
from shop_app.apis.shop_api import AddShopCartOperation, AddFavoritesOperation
from django.urls import path, include

app_name = 'Shop_app'

urlpatterns = [
    # path('add-into-shop-cart/', AddShopCartOperation.as_view(), name='add-into-shop-cart'),
    # path('add-into-favorites-chsc-api/', AddFavoritesOperation.as_view(), name='add-into-favorites-chsc-api'),
]



# DRF视图集注册
# router = routers.DefaultRouter()
# router.register('api/shop-chsc-search', CommoditySearchOperation, base_name="shop_chsc_search")
# urlpatterns += router.urls
