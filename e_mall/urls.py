"""e_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
# from django.views.generic import TemplateView
from e_mall import settings
from django.conf.urls.static import static
# from rest_framework.documentation import include_docs_urls


# 重要的是如下三行
from haystack.views import SearchView
from e_mall.base_view import error_404
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer

schema_view = get_schema_view(title='云逸电子商城开发接口文档', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('search/', SearchView(), name='search'),
    path('404/', error_404, name='404'),
    path('', include('mainsite.urls', namespace='mainsite')),
    # path('', TemplateView.as_view(template_name='index.html')),
    path('payment/', include('Payment_app.urls', namespace='payment')),
    path('shopper/', include('Shopper_app.urls', namespace='shopper')),
    path('consumer/', include('User_app.urls', namespace='consumer')),
    path('order/', include('Order_app.urls', namespace='order')),
    path('remark/', include('Remark_app.urls', namespace='remark')),
    path('shop/', include('Shop_app.urls', namespace='shop')),
    path('voucher/', include('Voucher_app.urls', namespace='voucher')),
    path('chsc-syz-247179876-docs/', schema_view, name='api_doc'),
    path(r'mdeditor/', include('mdeditor.urls')),
]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # 存放media资源
