from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter

from order_app.apis.order_api import OrderBasicOperation, OrderCreateOperation

app_name = 'order_app'

urlpatterns = [
    path(f'{settings.URL_PREFIX}/order-generation/', OrderCreateOperation.as_view(), name='order-create-chsc-api')
]

router = DefaultRouter()
router.register(f'{settings.URL_PREFIX}/order/', OrderBasicOperation, basename='order')
urlpatterns += router.urls
