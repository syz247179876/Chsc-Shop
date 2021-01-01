# -*- coding: utf-8 -*- 
# @Time : 2020/5/29 16:10 
# @Author : 司云中 
# @File : remark.py 
# @Software: PyCharm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url='/consumer/login/')
def personal_news(request):
    return render(request, 'news.html')


@login_required(login_url='/consumer/login/')
def personal_comment(request):
    return render(request, 'comment.html')
