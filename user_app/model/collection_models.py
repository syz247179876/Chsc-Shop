# -*- coding: utf-8 -*-
# @Time  : 2021/2/19 下午4:22
# @Author : 司云中
# @File : collection_models.py
# @Software: Pycharm
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _
from shop_app.models.commodity_models import Commodity

User = get_user_model()


class Collection(models.Model):
    """收藏夹"""

    # 用户
    user = models.ForeignKey(User, related_name='collections', on_delete=True, verbose_name=_('用户'))

    # 商品
    commodity = models.ForeignKey(Commodity, related_name='collections', on_delete=True, verbose_name=_('商品'),
                                       null=True)

    # 浏览时间
    collect_time = models.DateTimeField(auto_now_add=True, verbose_name=_('收藏时间'))

    # 逻辑删除
    fake_delete = models.BooleanField(default=False, verbose_name=_('逻辑删除'))

    objects = Manager()

    class Meta:
        db_table = 'collection'
        verbose_name = _('收藏夹')
        verbose_name_plural = _('收藏夹')
        ordering = ('collect_time',)
