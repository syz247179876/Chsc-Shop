# -*- coding: utf-8 -*-
# @Time  : 2020/9/12 下午11:44
# @Author : 司云中
# @File : voucher_models.py
# @Software: Pycharm


from django.contrib.auth.models import User
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from Shop_app.models.commodity_models import Commodity
from Shopper_app.models.shopper_models import Store


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


class Integral_commodity(models.Model):
    """积分商品表"""

    # 商品名
    # 商品名称
    commodity_name = models.CharField(verbose_name=_('商品名称'),
                                      help_text=_('Please enter the name of the product'),
                                      max_length=50,
                                      validators=[]
                                      )

    # 兑换积分值
    integral_price = models.PositiveIntegerField(verbose_name=_('积分值'))

    # 商品剩余量
    surplus = models.PositiveIntegerField(verbose_name=_('商品剩余量'), help_text=_('Quantity of merchandise exchanged'))

    integral_commodity_ = Manager()


    class Meta:
        db_table = 'Integral_commodity'
        verbose_name = _('积分商品表')
        verbose_name_plural = _('积分商品表')

    def __str__(self):
        return self.commodity_name

class BonusCategory(models.Model):

    category = models.CharField(verbose_name=_('红包种类'), max_length=15, help_text=_('创建新的红包类型'))

    # 是否审核
    is_check = models.BooleanField(default=True, verbose_name=_('是否审核'), help_text=_('红包类型是否审核？'))

    class Meta:
        db_table = 'BonusCategory'
        verbose_name = _('红包类别')
        verbose_name_plural = _('红包类别')
        ordering = ('category',)

class Bonus(models.Model):
    """红包类型映射类"""

    # 用户
    user = models.ForeignKey(User, related_name='bonus', verbose_name=_('当前用户'), on_delete=True)

    # # 红包类型
    # category_choice = (
    #     (1, '代金卷'),
    #     (2, '优惠卷'),
    #     (3, '积分红包'),
    #     (4, '商铺通用活动红包')
    # )

    category = models.OneToOneField(BonusCategory, verbose_name=_('红包类型'), help_text=_('选择红包的类型'), on_delete=True)

    # 红包标题
    bonus_title = models.CharField(max_length=20,verbose_name=_('红包标题'), help_text=_('需指明红包所属活动'))

    # 发放到某个店铺上
    store = models.ForeignKey(Store, related_name='bonus', on_delete=True, help_text=_('将红包发放到指定的商铺下'), null=True)

    # 发放到某个商品下
    commodity = models.ForeignKey(Commodity, related_name='bonus', on_delete=True, help_text=_('将红包发放到指定的商品下'), null=True)

    # 是否审核
    is_check = models.BooleanField(default=False, help_text=_('该红包是否被管理员审核？'), verbose_name=_('是否审核'))

    # 提交日期
    commit_time = models.DateTimeField(auto_now=True, help_text=_('红包申请提交的日期'), verbose_name=_('提交日期'))

    # 审核完毕日期
    audit_time = models.DateTimeField(auto_now_add=True, help_text=_('管理员审核完毕日期'), verbose_name=_('审核日期'))

    # 是否发放红包
    is_grant = models.BooleanField(default=False, help_text=_('是否发放空包？'), verbose_name=_('是否发放红包'))

    # 是否限制红包数量
    is_limit_counts = models.BooleanField(default=False, help_text=_('是否对红包数量有限制？'), verbose_name=_('是否限制红包数量'))

    # 红包数量
    counts = models.PositiveIntegerField(default=0, help_text=_('红包数量'), verbose_name=_('红包数量'))


    class Meta:
        db_table = 'Bonus'
        verbose_name = _('红包')
        verbose_name_plural = _('红包类型')
        ordering = ('-commit_time',)


    def __str__(self):
        return self.bonus_title
