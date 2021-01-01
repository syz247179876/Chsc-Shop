from payment_app.apis.payment_api import PaymentOperation, UpdateOperation
from django.urls import path, include

app_name = 'payment_app'

urlpatterns = [
    path('payment', PaymentOperation.as_view(), name='payment-chsc-api'),  # 创建订单，调用alipay
    # path('update-order-chsc-api/', UpdateOperation.as_view(), name='update-order-chsc-api/')  # 相应alipay请求，更新订单
]

