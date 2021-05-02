# -*- coding: utf-8 -*-
# @Time  : 2021/2/10 下午12:59
# @Author : 司云中
# @File : urls.py
# @Software: Pycharm
from django.conf import settings
from django.urls import path, include

from manager_app.apis.auth_api import ManagerLoginApiView, ManagerRegisterApiView
from manager_app.apis.manage_carousel_api import ManageCarouselApiView
from manager_app.apis.manage_commodity_api import ManagerCommodityCategoryApiView, ManageCommodityGroupApiView
from manager_app.apis.manage_permission_api import ManagePermissionApiView
from manager_app.apis.manage_role_api import ManageRoleApiView
from manager_app.apis.manage_seller_api import ManagerSellerPermApiView, ManagerSellerRoleApiView

app_name = "manager_app"

auth_patterns = [
    path('login/', ManagerLoginApiView.as_view()),
    path('register/', ManagerRegisterApiView.as_view()),
]

urlpatterns = {
    path(f'{settings.URL_PREFIX}/auth/', include(auth_patterns)),
    path(f'{settings.URL_PREFIX}/role/', ManageRoleApiView.as_view()),
    path(f'{settings.URL_PREFIX}/permission/', ManagePermissionApiView.as_view()),
    path(f'{settings.URL_PREFIX}/commodity-category/', ManagerCommodityCategoryApiView.as_view()),
    path(f'{settings.URL_PREFIX}/commodity-group/', ManageCommodityGroupApiView.as_view()),
    path(f'{settings.URL_PREFIX}/role/seller/', ManagerSellerRoleApiView.as_view()),
    path(f'{settings.URL_PREFIX}/permission/seller/', ManagerSellerPermApiView.as_view()),
    path(f'{settings.URL_PREFIX}/carousel/', ManageCarouselApiView.as_view())
}
