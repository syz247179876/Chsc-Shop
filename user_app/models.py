# -*- coding: utf-8 -*-
# @Time : 2020/5/8 18:37
# @Author : 司云中
# @File : models.py
# @Software: PyCharm
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import Manager
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from shop_app.models.commodity_models import Commodity
from user_app.model.seller_models import Store
from user_app.utils.validators import RecipientsValidator, RegionValidator, PhoneValidator, AddressTagValidator


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_superuser(self, username, email, password, **extra_fields):
        """
        创建超级管理员，审核重要issue
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        password = make_password(password)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def _create_user(self, **extra_fields):
        """
        通过手机创建用户
        :param phone: 用户名
        :param extra_fields: 额外字段
        :return: user对象
        """
        user = self.model(**extra_fields)
        user.save(using=self._db)
        return user

    def _check_user_existed(self, **extra_fields):
        return self.filter(extra_fields).count() > 0

    def create_consumer(self, password=None, **extra_fields):
        extra_fields.setdefault('is_seller', False)
        extra_fields.setdefault('is_superuser', False)
        password = make_password(password)
        return self._create_user(password=password, **extra_fields)

    def create_seller(self, password=None, **extra_fields):
        extra_fields.setdefault('is_seller', True)
        extra_fields.setdefault('is_stuff', True)
        extra_fields.setdefault('is_superuser', False)
        password = make_password(password)
        return self._create_user(password=password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_seller', False)
        extra_fields.setdefault('is_stuff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_seller') is True:
            raise ValueError('Superuser must not have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_superuser(username, email, password, **extra_fields)

    def check_user_existed(self, **extra_fields):

        return self._check_user_existed(**extra_fields)


class AbstractUser(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('昵称'),
        max_length=30,
        unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    full_name = models.CharField(_('姓名'), max_length=10, blank=True, null=True)
    email = models.EmailField(
        _('邮箱'),
        blank=True,
        null=True,
        unique=True, error_messages={
            'unique': _("A user with that email already exists")
        })
    phone = models.CharField(
        _('手机号'),
        blank=True,
        null=True,
        max_length=11,
        validators=[PhoneValidator],
        error_messages={
            'unique': _('A user with that email already exists')
        })

    is_seller = models.BooleanField(
        _('卖家身份'),
        default=False,
        help_text=_(
            'Consumer upgrade to sellers by registering to open store'
            'who have access to the background'
        ),
    )

    is_staff = models.BooleanField(
        _('销售员工'),
        default=False,
        help_text=_(
            'Consumer upgrade to sellers by registering to open store'
            'who have access to the background'
        ),
    )

    is_active = models.BooleanField(
        _('激活状态'),
        default=True,
        help_text=_(
            'Stranger who has registered to become users'
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    # 是否是系统管理员
    is_manager = models.BooleanField(
        _('系统管理员'),
        default=False,
        help_text=_(
            'Manager of this system who possess the highest priority of the whole operation'
            ', whose duty is to keep system running well and take some extra essential operation '
            'to publish message to all sellers!'
        )
    )

    birthday = models.DateField(
        _('出生日期'),
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
        default='s',
        choices=sex_choice,
        max_length=1,
    )

    head_image = models.ImageField(
        verbose_name=_('头像'),
        null=True,
        blank=True,
    )

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    PHONE_FILED = 'phone'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone']

    class Meta:
        db_table = 'User'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        返回first
        """
        return self.full_name

    def head_images(self):
        # 这里添加一个防空判断
        if not self.head_image:
            return '无'
        else:
            return format_html("<img src='{}' style='width:50px;height:50px;'>",
                               self.head_image.url,
                               self.head_image)

    head_images.short_description = '头像'


class User(AbstractUser):
    """
    Users within the Django authentication system are represented by this
    model.

    Username and password are required. Other fields are optional.
    """

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'


class Consumer(models.Model):
    """用户表"""
    # 用户名
    user = models.OneToOneField(
        User,
        verbose_name=_('消费者'),
        on_delete=models.CASCADE,
        related_name='consumer',
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

    nationality = models.CharField(
        _('详细地址'),
        help_text=_('详细地址信息'),
        max_length=30,
        null=True,
        blank=True
    )

    integral = models.PositiveIntegerField(
        _('积分值'),
        default=0
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
        return self.user.get_username()

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
    commodity = models.ForeignKey(Commodity, related_name='collections', verbose_name=_('商品'), on_delete=True,
                                  null=True)

    # 店铺
    store = models.ForeignKey(Store, related_name='store', verbose_name=_('店铺'), on_delete=True, null=True)

    # 浏览时间
    datetime = models.DateTimeField(auto_now_add=True, verbose_name=_('收藏时间'))

    collection_ = Manager()

    class Meta:
        db_table = 'Collection'
        verbose_name = _('收藏夹')
        verbose_name_plural = _('收藏夹')
        ordering = ('datetime',)

    def __str__(self):
        """对模型进行序列化"""
        return {
            'user': self.user
        }
