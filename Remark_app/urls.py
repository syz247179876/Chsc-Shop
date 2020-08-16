from rest_framework.routers import DefaultRouter

from Remark_app.views.remark import personal_comment, personal_news


from django.urls import path, include

from Remark_app.views.remark_api import RemarkOperation

app_name = 'Remark_app'

urlpatterns = [
    path('personal_comment/', personal_comment, name='personal_comment'),
    path('personal_news/', personal_news, name='personal_news'),
]

router = DefaultRouter()
router.register(r'remark-chsc-api', RemarkOperation, basename='remark')
urlpatterns += router.urls
