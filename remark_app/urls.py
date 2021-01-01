from rest_framework.routers import DefaultRouter

from remark_app.views.remark_api import RemarkOperation, AttitudeRemarkOperation
from django.conf import settings
app_name = 'Remark_app'

urlpatterns = [
]

router = DefaultRouter()
router.register(f'{settings.URL_PREFIX}/remark', RemarkOperation, basename='remark')
router.register(f'{settings.URL_PREFIX}/attitude', AttitudeRemarkOperation, basename='remark-attitude')
urlpatterns += router.urls
