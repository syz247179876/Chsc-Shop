from Remark_app.views.remark import personal_comment, personal_news
from Remark_app.views.remark_api import RemarkOperation

from django.urls import path, include

app_name = 'Remark_app'

urlpatterns = [
    path('personal_comment/', personal_comment, name='personal_comment'),
    path('personal_news/', personal_news, name='personal_news'),
    path('remark-operation-chsc-api/', RemarkOperation.as_view(), name='remark-operation-chsc-api/'),
]
