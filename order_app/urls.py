from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter

from order_app.apis.order_api import OrderBasicOperation, OrderConfirmOperation

app_name = 'order_app'

urlpatterns = [
    path(f'{settings.URL_PREFIX}/confirmation/', OrderConfirmOperation.as_view(), name='order-confirm'),
]

router = DefaultRouter()
router.register(f'{settings.URL_PREFIX}/order', OrderBasicOperation, basename='order')
urlpatterns += router.urls
