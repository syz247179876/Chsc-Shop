from django.urls import path
from mainsite.views.home import home_page
from mainsite.views.home_api import GoodsHomeOperation

app_name = 'mainsite'

urlpatterns = [
    path('', home_page, name='home_page'),
    path('home-operation-chsc-api/', GoodsHomeOperation.as_view(), name='HomeOperation'),
]
