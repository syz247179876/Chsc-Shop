# -*- coding: utf-8 -*-
# @Time  : 2020/11/20 上午12:00
# @Author : 司云中
# @File : oauth_models.py
# @Software: Pycharm
from django.contrib.auth import get_user_model

User = get_user_model()

from django.db import models

class OauthQQ(models.Model):
    user = models.ForeignKey(User,on_delete=True,related_name='qq', verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'qq_oauth'
        verbose_name = 'QQ第三方登录'
        verbose_name_plural = verbose_name

class OauthWeiXin(models.Model):
    ser = models.ForeignKey(User, on_delete=True, related_name='wx', verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'wx_oauth'
        verbose_name = '微信第三方登录'
        verbose_name_plural = verbose_name

