from Shopper_app.views.shopper_api import ShopperOperation
from django.urls import path, include

app_name = 'Shopper_app'

urlpatterns = [
    # path('register/', RedisShopperOperation.as_view(), name='register'),
    # path('verification-code/', Verification_code.as_view(), name='verification-code'),
    path('shopper-operation-chsc-api/', ShopperOperation.as_view(), name='shopper-operation-chsc-api'),
]
