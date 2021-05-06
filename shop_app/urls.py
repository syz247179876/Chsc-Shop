from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter

from shop_app.apis.carousel_api import CarouselApiView
from shop_app.apis.display_api import CommodityCardDisplay, CommodityDetailDisplay, CommodityCategoryDisplay

app_name = 'shop_app'

urlpatterns = [
    path(f'{settings.URL_PREFIX}/crousel/', CarouselApiView.as_view()),
    # path('add-into-shop-cart/', AddShopCartOperation.as_view(), name='add-into-shop-cart'),
    # path('add-into-favorites-chsc-api/', AddFavoritesOperation.as_view(), name='add-into-favorites-chsc-api'),
]


# DRF视图集注册
router = DefaultRouter()
router.register(f'{settings.URL_PREFIX}', CommodityCardDisplay, basename='commodity-card')  # 关键词搜索/商品卡片显示
router.register(f'{settings.URL_PREFIX}', CommodityDetailDisplay, basename='commodity-detail')   # 商品详情显示
router.register(f'{settings.URL_PREFIX}', CommodityCategoryDisplay, basename='commodity-category'),  # 商品类别
urlpatterns += router.urls
