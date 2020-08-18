# -*- coding: utf-8 -*-
# @Time  : 2020/8/18 下午8:50
# @Author : 司云中
# @File : __init__.py.py
# @Software: Pycharm
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from Shop_app.models.commodity_models import Commodity


class Integrals(models.Model):
    """积分表"""

    # 消费者
    user = models.OneToOneField(User, on_delete=True, related_name='integral', verbose_name=_('用户'))

    # 某次消费获得的积分
    fraction = models.PositiveIntegerField(verbose_name=_('积分'), default=0)

    # 某次消费的商品
    commodity = models.ForeignKey(Commodity, on_delete=False, related_name='integral', verbose_name=_('购买的商品'))

    # 某次消费的商品种类
    category = models.CharField(verbose_name=_('商品种类'), max_length=10)

    # 消费时间
    consumer_time = models.DateTimeField(verbose_name=_('消费时间'), auto_now_add=True)

    integral_ = Manager()

    class Meta:
        db_table = 'Integral'
        verbose_name = _('积分表')
        verbose_name_plural = _('积分表')

    def __str__(self):
        return '用户:{}'.format(self.user.get_username())
