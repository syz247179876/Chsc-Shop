# -*- coding: utf-8 -*-
# @Time  : 2020/8/23 下午6:29
# @Author : 司云中
# @File : shopcart_models.py
# @Software: Pycharm
from seller_app.models import Store
from user_app.models import User
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from shop_app.models.commodity_models import Commodity


class Trolley(models.Model):
    """购物车"""

    # 用户
    user = models.ForeignKey(User, verbose_name=_('用户'), on_delete=True, related_name='trolley')

    # 商品
    commodity = models.ForeignKey(Commodity, verbose_name=_('商品'), on_delete=True, related_name='trolley')

    # 加入时间
    time = models.DateTimeField(auto_now_add=True)

    # 该商品数量
    count = models.PositiveIntegerField(verbose_name=_('商品数量'),default=1)

    # 该商品价格
    price = models.DecimalField(verbose_name=_('商品价格'), decimal_places=2, max_digits=11)

    # 店铺
    store = models.ForeignKey(Store, verbose_name=_('店铺'), on_delete=True, related_name='trolley')

    trolley_ = Manager()

    class Meta:
        db_table = 'trolley'
        verbose_name = _('购物车')
        verbose_name_plural = _('购物车')
        ordering = ('time',)
