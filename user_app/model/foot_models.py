# -*- coding: utf-8 -*-
# @Time  : 2021/2/19 下午4:22
# @Author : 司云中
# @File : foot_models.py
# @Software: Pycharm
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _
from shop_app.models.commodity_models import Commodity
User = get_user_model()

class Foot(models.Model):
    """用户足迹表"""

    # 用户
    user = models.ForeignKey(User, related_name='foots', on_delete=True, verbose_name=_('用户'))

    # 商品
    commodity = models.ManyToManyField(Commodity, related_name='foots', verbose_name=_('商品'))

    # 浏览次数
    view_counts = models.PositiveIntegerField(default=0, verbose_name=_('浏览次数'))

    objects = Manager()

    class Meta:
        db_table = 'Foot'
        verbose_name = _('足迹')
        verbose_name_plural = _('足迹')
        ordering = ('view_counts',)

    def __str__(self):
        return '浏览商品id:{}'.format(self.commodity)
