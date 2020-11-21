# -*- coding: utf-8 -*-
# @Time  : 2020/11/20 上午12:00
# @Author : 司云中
# @File : oauth_models.py
# @Software: Pycharm

from django.contrib.auth import get_user_model
from django.db.models import Manager

User = get_user_model()

from django.db import models

class QqManager(Manager):
    """QQ登录模型管理类"""

    def existed_user(self, openid):
        """
        判断用户是否存在
        :param openid: openid用户唯一标识
        :return:用户对象 or None
        """
        try:
            return self.select_related('user').get(openid=openid)  # 返回用户对象
        except type(self).DoesNotExist:
            return None   # 用户不存在返回None

    def create_qq_user(self, user, open_id):
        """
        用户第一次使用QQ登录,绑定创建对象
        :return: qq_user
        """
        try:
            user = self.get(open_id=open_id)
            return None
        except User.objects.DoesNotExist:
            # 如果没有该用户尚未绑定任何QQ帐号,则创建
            return self.create(user=user, openid=open_id)


class WxManager(Manager):
    """微信登录模型管理类"""

    pass


class OauthQQ(models.Model):
    user = models.ForeignKey(User,on_delete=True,related_name='qq', verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    qq_manager = QqManager()

    class Meta:
        db_table = 'qq_oauth'
        verbose_name = 'QQ第三方登录'
        verbose_name_plural = verbose_name

class OauthWeiXin(models.Model):
    ser = models.ForeignKey(User, on_delete=True, related_name='wx', verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    qq_manager = Manager()

    class Meta:
        db_table = 'wx_oauth'
        verbose_name = '微信第三方登录'
        verbose_name_plural = verbose_name

