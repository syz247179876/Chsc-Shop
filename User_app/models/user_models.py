# -*- coding: utf-8 -*-
# @Time : 2020/5/8 18:37
# @Author : 司云中
# @File : user_models.py
# @Software: PyCharm
from Shop_app.models.commodity_models import Commodity
from User_app.validators import RecipientsValidator, RegionValidator, PhoneValidator, AddressTagValidator
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _


class Consumer(models.Model):
    """用户表"""
    # 用户名
    user = models.OneToOneField(
        User,
        verbose_name=_('消费者'),
        on_delete=models.CASCADE,
        related_name='consumer',
    )

    # 头像,会上传到media中的head目录下，不需要下划线，因为setting中的media已经有下划线了,
    head_image = models.ImageField(
        verbose_name=_('头像'),
        help_text=_('上传您的头像'),
        upload_to='head',
        null=True,
        blank=True,
    )

    birthday = models.DateField(
        _('生日'),
        help_text=_('填写您的出生日期'),
        null=True,
        blank=True,
    )

    sex_choice = (
        ('m', '男'),
        ('f', '女'),
        ('s', '保密')
    )

    sex = models.CharField(
        verbose_name=_('性别'),
        help_text=_('填写您的性别'),
        default='s',
        choices=sex_choice,
        max_length=1,
    )

    phone = models.CharField(
        _('手机号'),
        help_text=_('填写您的手机号'),
        max_length=11,
        blank=True,
        null=True,
    )

    rank_choice = (
        ('1', '先锋会员'),
        ('2', '卫士会员'),
        ('3', '中军会员'),
        ('4', '统帅会员'),
        ('5', '传奇会员'),
        ('6', '万古流芳会员'),
        ('7', '超凡入圣会员'),
        ('8', '冠绝一世会员'),
    )

    rank = models.CharField(
        _('会员等级'),
        help_text=_('您的会员等级'),
        max_length=1,
        default=1,
        choices=rank_choice
    )

    safety = models.DecimalField(
        _('安全分数'),
        help_text=_('您的信息安全分数'),
        decimal_places=0,
        max_digits=3,
        default=60,
    )

    USER_FIELD = 'user'
    PHONE_FIELD = 'phone'
    HEAD_IMAGE_FIELD = 'head_image'
    SEX_FIELD = 'sex'

    consumer_ = Manager()

    class Meta:
        db_table = 'Consumer'
        verbose_name = _('消费者')
        verbose_name_plural = _('消费者')
        # permissions = [('can_view_address','can_v')]

    def __str__(self):
        return self.user

    @property
    def get_username(self):
        """get username for this User"""
        user = getattr(self, self.USER_FIELD)
        return user.get_username()

    @property
    def get_email(self):
        """get email for this User"""
        user = getattr(self, self.USER_FIELD)
        return user.get_email()

    @property
    def get_phone(self):
        """get email for this User"""
        phone = getattr(self, self.PHONE_FIELD)
        if not phone:
            return ''
        return phone

    @property
    def get_head_image(self):
        """get head image for this User"""
        head_image = getattr(self, self.HEAD_IMAGE_FIELD)
        if not head_image:
            return ''
        return head_image


class Address(models.Model):
    """收货地址"""
    # 用户，一个用户多个收货地址
    user = models.ForeignKey(User, verbose_name=_("消费者"),
                             on_delete=models.CASCADE,
                             related_name='address')
    # 收件人
    recipients = models.CharField(verbose_name=_('收件人'),
                                  max_length=20,
                                  validators=[RecipientsValidator(), ]
                                  )

    # 收件地址，所在地区,后期改成下拉列表的形式
    region = models.CharField(verbose_name=_('所在地区'),
                              max_length=50,
                              validators=[RegionValidator(), ]
                              )
    # 地址标签
    address_tags_choice = (
        ('1', '家'),
        ('2', '公司'),
        ('3', '学校'),
    )
    address_tags = models.CharField(verbose_name=_('地址标签'),
                                    max_length=1,
                                    choices=address_tags_choice,
                                    validators=[AddressTagValidator(), ],
                                    )
    # 是否设置为默认地址
    default_address = models.BooleanField(verbose_name=_('默认地址'),
                                          default=False)

    # 手机号，必须
    phone = models.CharField(verbose_name=_('手机号'),
                             help_text=_('Please write your cell-phone number'),
                             error_messages={
                                 'unique': _('A telephone number with this already exists.'),
                             },
                             validators=[PhoneValidator(), ],
                             max_length=11,
                             )

    address_ = Manager()

    class Meta:
        db_table = 'Address'
        verbose_name = _('收获地址')
        verbose_name_plural = _('收获地址')
        ordering = ('-default_address',)

    def __str__(self):
        return self.recipients


class Foot(models.Model):
    """用户足迹表"""

    # 用户
    user = models.ForeignKey(User, related_name='foots', on_delete=True, verbose_name=_('用户'))

    # 商品
    commodity = models.ManyToManyField(Commodity, related_name='foots', verbose_name=_('商品'))

    # 浏览时间
    time = models.DateField(auto_now_add=True, verbose_name=_('浏览时间'))

    class Meta:
        db_table = 'Foot'
        verbose_name = _('足迹')
        verbose_name_plural = _('足迹')
        ordering = ('time',)

    def __str__(self):
        return '浏览商品id:{}'.format(self.commodity)


class Collection(models.Model):
    """收藏夹"""

    # 用户
    user = models.ForeignKey(User, related_name='collections', on_delete=True, verbose_name=_('用户'))

    # 商品
    commodity = models.ManyToManyField(Commodity, related_name='collections', verbose_name=_('商品'))

    # 浏览时间
    time = models.DateField(auto_now_add=True, verbose_name=_('收藏时间'))

    class Meta:
        db_table = 'Collection'
        verbose_name = _('收藏夹')
        verbose_name_plural = _('收藏夹')
        ordering = ('time',)

    def __str__(self):
        return '收藏商品id:{}'.format(self.commodity)



