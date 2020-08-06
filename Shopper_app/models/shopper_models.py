from django.contrib.auth.models import User
from django.db import models
from django.db.models import Manager
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from Shopper_app.validators import validate_sex, PhoneValidator


class Shoppers(models.Model):
    """店家表"""

    user = models.OneToOneField(
        User,
        verbose_name=_('商家id'),
        on_delete=models.CASCADE,
        related_name='shoppers',
    )

    phone = models.CharField(
        verbose_name=_('手机号'),
        unique=True,
        validators=[PhoneValidator(), ],
        max_length=11
    )
    shop_credit_choice = (
        ('1', '1星'),
        ('2', '2星'),
        ('3', '3星'),
        ('4', '4星'),
        ('5', '5星'),
        ('6', '1钻'),
        ('7', '2钻'),
        ('8', '3钻'),
        ('9', '4钻'),
        ('10', '5钻'),
    )
    credit = models.CharField(
        verbose_name=_('信誉'),
        help_text=_('您的信誉等级'),
        choices=shop_credit_choice,
        default=1,
        max_length=1,
    )
    sex_choice = (
        ('m', '男'),
        ('f', '女'),
    )
    sex = models.CharField(
        verbose_name=_('性别'),
        help_text=_('性别'),
        blank=True,
        choices=sex_choice,
        max_length=1,
        validators=[validate_sex, ]
    )
    # 头像

    head_image = models.ImageField(verbose_name=_('头像'),
                                   help_text=_('Please upload your portrait'),
                                   upload_to='head',
                                   null=True,
                                   blank=True,
                                   )

    category_choice = (
        ('衣服', '衣服'),
        ('裤子', '裤子'),
        ('生活用品', '生活用品'),
        ('家具', '家具'),
        ('鞋子', '鞋子'),
        ('化妆品', '化妆品'),
        ('零食', '零食')
    )
    # 销售商品的类别
    sell_category = models.CharField(choices=category_choice, max_length=10,
                                     default='衣服')

    # 具体住址
    nationality = models.CharField(max_length=50, default='')

    def head_images(self):
        # 这里添加一个防空判断
        if not self.head_image:
            return '无'
        else:
            return format_html("<img src='{}' style='width:50px;height:50px;'>",
                               self.head_image.url,
                               self.head_image)

    head_images.short_description = '头像'

    is_vip = models.BooleanField(_('是否是vip'), default=True)

    birthday = models.DateField(
        _('生日'),
        help_text=_('填写您的出生日期'),
        null=True,
        blank=True,
    )

    shopper_ = Manager()

    PHONE_FIELD = 'phone'
    USER_FIELD = 'user'

    class Meta:
        verbose_name = _('商家')
        verbose_name_plural = _('商家')

    def get_username(self):
        """get user"""
        user = getattr(self, self.USER_FIELD)
        return user.get_username()

    def get_email(self):
        """get email"""
        user = getattr(self, self.USER_FIELD)
        return user.get_email_field_name()

    def get_phone(self):
        """get mobile phone"""
        return getattr(self, self.PHONE_FIELD)


class Store(models.Model):
    """店铺表"""
    # 店铺名称
    store_name = models.CharField(verbose_name=_('店铺'),
                                  help_text=_('请定义您的商铺名，默认为您的有户名+"的商铺"'),
                                  max_length=30,
                                  )
    # 商家
    shopper = models.OneToOneField(User,
                                   verbose_name=_('商家'),
                                   on_delete=models.CASCADE,
                                   related_name='store',
                                   )

    # 注册时间
    start_time = models.DateTimeField(verbose_name=_('注册时间'), auto_now_add=True)

    # 销售地  省
    # 通过get_字段_display()显示choice中的后半部分

    province = models.CharField(verbose_name=_('省份'),
                                help_text=_('请填写您的省份'),
                                max_length=10,
                                blank=True
                                )
    # 销售地  市
    city = models.CharField(verbose_name=_('城市'),
                            help_text=_('请填写您的城市'),
                            max_length=10,
                            blank=True)

    # 被关注量
    attention = models.PositiveIntegerField(verbose_name=_('关注量'),
                                            default=0,
                                            )

    # 店铺评分,max_digits表示最大位数，decimal_places=1表示精度（小数)位数
    shop_grade = models.DecimalField(verbose_name=_('店铺评分'),
                                     max_digits=2,
                                     decimal_places=1,
                                     default=0.0,
                                     )

    store_ = Manager()

    def __str__(self):
        return self.store_name

    class Meta:
        verbose_name = _('店铺')
        verbose_name_plural = _('店铺')


'''
class Ip(mongoengine.):
    """Ip表"""
    # 登录总次数
    ips = models.CharField(verbose_name=_('ip地址'),
                           help_text=_('ip地址'),
                           max_length=12,
                           )
    # 当前日期
    login_time = models.DateTimeField(verbose_name=_('上线时间'),
                                      help_text=_('登录的时间'),
                                      auto_now_add=True,
                                      )
    # 商家
    shopper = models.ForeignKey(User, verbose_name=_('商家'),
                                help_text=_('商家'),
                                on_delete=models.CASCADE,
                                related_name='ip')
    # 下线时间
    exit_time = models.DateTimeField(verbose_name=_('下线时间'),
                                     help_text=_('退出网站的时间'),
                                     blank=True,
                                     )

    ip_ = Manager()

    class meta:
        ordering = ('-date')
        verbose_name = _('记录表')
        verbose_name_plural = _('记录表')

    def __str__(self):
        return self.ips
'''
