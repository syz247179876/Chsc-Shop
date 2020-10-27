from rest_framework.routers import DefaultRouter

from user_app.views.edge_api import record_browsing_login, record_browsing_every
from user_app.views.login_register_api import RegisterAPIView, LoginAPIView
from user_app.views.personal_api import *
from user_app.views.verification_code import VerificationCodeBind, \
    VerificationCodeRegister, VerificationCodeModifyPassword, VerificationCodeShopperOpenStore
from user_app.views.views import register_page, login_page
from user_app.views.personal import *
from django.urls import path


app_name = 'user_app'

urlpatterns = [
    # path('login/', login_page, name='login'),
    # path('register/', register_page, name='register'),
    # path('logout/', logout_mall, name='logout'),
    # path('personal/', personal, name='personal'),
    # path('personal_information/', personal_information, name='personal_information'),
    # path('personal_address/', personal_address, name='personal_address'),
    # path('personal_bill/', personal_bill, name='personal_bill'),
    # path('personal_bonus/', personal_bonus, name='personal_bonus'),
    # path('personal_foot/', personal_foot, name='personal_foot'),
    # path('personal_coupon/', personal_coupon, name='personal_coupon'),
    # path('personal_shopcart/', personal_shopcart, name='personal_shopcart'),
    # path('personal_collection/', personal_collection, name='personal_collection'),
    # path('personal_safety/', personal_safety, name='personal_safety'),
    # path('personal_password/', personal_password, name='personal_password'),
    # path('personal_setpay/', personal_setpay, name='personal_setpay'),
    # path('personal_bindphone/', personal_bindphone, name='personal_bindphone'),
    # path('personal_bindemail/', personal_bindemail, name='personal_bindemail'),
    # path('personal_idcard/', personal_idcard, name='personal_idcard'),
    # path('personal_question/', personal_question, name='personal_question'),
    # path(r'personal_edit_address/chsc_p=<str:pk>/', edit_address, name='edit_address'),

    path('record-browser-login-api/', record_browsing_login, name='record-browser-login'),
    path('record-browser-api/', record_browsing_every, name='record-browser'),
    path('login-chsc-api/', LoginAPIView.as_view(), name='login-chsc-api'),
    path('register-chsc-api/', RegisterAPIView.as_view(), name='register-chsc-api'),
    path('verification-code-chsc-register-api/', VerificationCodeRegister.as_view(), name='verification-code-chsc-register-api'),
    # path('Verification-code-pay-chs-api/', VerificationCodePay.as_view(), name='Verification-code-pay-chs-api'),
    path('verification-code-chsc-open-store-api/', VerificationCodeShopperOpenStore.as_view(), name='verification-code-chsc-open-store-api'),
    path('verification-code-chsc-bind-api/', VerificationCodeBind.as_view(), name='verification-code-chsc-bind-api'),
    path('verification-code-chsc-modify-pwd-api/', VerificationCodeModifyPassword.as_view(),
         name='verification-code-chsc-modify-pwd-api'),
    path('information-chsc-api/', SaveInformation.as_view(), name='information-changes-chsc-api'),
    path('password-changes-chsc-api/', ChangePassword.as_view(), name='password-changes-chsc-api'),
    path('email-or-phone-binding-chsc-api/', BindEmailOrPhone.as_view(), name='email-or-phone-binding-chsc-api'),
    path('verification-name-chsc-api/', VerifyIdCard.as_view(), name='verification-name-chsc-api'),
    path('shop-head-image-chsc-api/', HeadImageOperation.as_view(), name='shop-head-image-chsc-api'),
]



router = DefaultRouter()
router.register(r'address-chsc-api', AddressOperation, basename='address')
router.register(r'foot-chsc-api', FootOperation, basename='foot')
router.register(r'favorites-chsc-api', FavoriteOperation, basename='favorites')
router.register(r'trolley-chsc-api', ShopCartOperation, basename='trolley')
urlpatterns += router.urls
