from django.urls import path

from django.conf import settings

from shop_app.apis.carousel_api import CarouselApiView

app_name = 'shop_app'

urlpatterns = [
    path(f'{settings.URL_PREFIX}/crousel/', CarouselApiView.as_view()),
    # path('add-into-shop-cart/', AddShopCartOperation.as_view(), name='add-into-shop-cart'),
    # path('add-into-favorites-chsc-api/', AddFavoritesOperation.as_view(), name='add-into-favorites-chsc-api'),
]



# DRF视图集注册
# router = routers.DefaultRouter()
# router.register('api/shop-chsc-search', CommoditySearchOperation, base_name="shop_chsc_search")
# urlpatterns += router.urls
