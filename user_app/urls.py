from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user_app.apis.address_api import AddressOperation
from user_app.apis.auth_api import RegisterAPIView, LoginAPIView
from user_app.apis.bind_api import BindEmailOrPhone
from user_app.apis.cart_api import ShopCartOperation
from user_app.apis.foot_api import FootOperation
from user_app.apis.head_image_api import HeadImageOperation
from user_app.apis.information_api import InformationOperation
from user_app.apis.ocr_api import VerifyIdCard
from user_app.apis.password_api import ChangePassword
from django.conf import settings

from user_app.apis.password_api import RetrievePasswordOperation, NewPassword

app_name = 'user_app'

# 认证子路由
auth_patterns = [
    path('login/', LoginAPIView.as_view()),
    path('register/', RegisterAPIView.as_view())
]

# 密码操作子路由
password_patterns = [
    path('changable/', ChangePassword.as_view()),
    path('retrievable/', RetrievePasswordOperation.as_view()),
    path('renewable/', NewPassword.as_view()),
]

# 个人信息子路由
information_patterns = [
    path('password/', include(password_patterns)),
    path('detail/', InformationOperation.as_view()),
    path('binding/', BindEmailOrPhone.as_view()),
    path('identity/', VerifyIdCard.as_view()),
    path('head-image/', HeadImageOperation.as_view()),
]

urlpatterns = [
    path(f'{settings.URL_PREFIX}/auth/', include(auth_patterns)),
    path(f'{settings.URL_PREFIX}/information/', include(information_patterns)),
]

router = DefaultRouter()
router.register(f'{settings.URL_PREFIX}/address', AddressOperation, basename='address')
router.register(f'{settings.URL_PREFIX}/foot', FootOperation, basename='foot')
# router.register(f'{settings.URL_PREFIX}/favorites', FavoriteOperation, basename='favorites')
router.register(f'{settings.URL_PREFIX}/trolley', ShopCartOperation, basename='trolley')
urlpatterns += router.urls
