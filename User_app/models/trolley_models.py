# -*- coding: utf-8 -*-
# @Time  : 2020/8/23 下午6:29
# @Author : 司云中
# @File : shopcart_models.py
# @Software: Pycharm
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from Shop_app.models.commodity_models import Commodity
from Shopper_app.models.shopper_models import Store


class Trolley(models.Model):
    user = models.ForeignKey(User, verbose_name=_('用户'), on_delete=True, related_name='trolley')

    commodity = models.ForeignKey(Commodity, verbose_name=_('商品'), on_delete=True, related_name='trolley')

    store = models.ForeignKey(Store, verbose_name=_('店铺'), on_delete=True, related_name='trolley')

    time = models.DateTimeField(auto_now_add=True)

    trolley_ = Manager()

    class Meta:
        db_table = 'Trolley'
        verbose_name = _('购物车')
        verbose_name_plural = _('购物车')
        ordering = ('-time',)
