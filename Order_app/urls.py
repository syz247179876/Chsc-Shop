from Order_app.views.order import personal_order, personal_generate_order
from Order_app.views.order_api import OrderBasicOperation, OrderCommitOperation, OrderBuyNow
from User_app.views.personal import personal_change
from django.urls import path, include

app_name = 'Order_app'

urlpatterns = [
    path('personal_order/', personal_order, name='personal_order'),
    path('personal_change/', personal_change, name='personal_change'),
    path('personal_generate_order/', personal_generate_order, name='personal_generate_order'),
    path('order-chsc-api/', OrderBasicOperation.as_view(), name='order-chsc-api'),
    # path('order-refund-chsc-api/', OrderBasicRefund.as_view(), name='order-refund-chsc-api'),
    path('order-buy-now-chsc-api/', OrderBuyNow.as_view(), name='order-buy-now-chsc-api'),
    path('get-order-commodity-chsc-api/', OrderCommitOperation.as_view(), name='get-order-commodity-chsc-api')
]
